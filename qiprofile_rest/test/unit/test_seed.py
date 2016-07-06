from nose.tools import (assert_is_none, assert_is_instance, assert_in,
                        assert_is_not_none, assert_true, assert_false,
                        assert_equal)
from datetime import datetime
from mongoengine import connect
from qiprofile_rest_client.model.subject import Subject
from qiprofile_rest_client.model.uom import Weight
from qiprofile_rest_client.model.clinical import (Biopsy, Surgery, Drug)
from qiprofile_rest.test.helpers import seed

MODELING_RESULT_PARAMS = ['fxl_k_trans', 'fxr_k_trans', 'delta_k_trans', 'v_e', 'tau_i']
"""The test seed modeling result parameters."""


class TestSeed(object):
    """
    This TestSeed class tests the seed helper utility.

    Note: this test drops the ``qiprofile-test`` Mongo database
    at the beginning and end of execution.
    """
    def setup(self):
        self._connection = connect(db='qiprofile_test')
        self._connection.drop_database('qiprofile_test')
        self._subjects = seed.seed()

    def tearDown(self):
        self._connection.drop_database('qiprofile_test')

    def test_serialization(self):
        for saved_sbj in self._subjects:
            query = dict(project=saved_sbj.project,
                         collection=saved_sbj.collection,
                         number=saved_sbj.number)
            fetched_sbj = Subject.objects.get(**query)
            self._validate_subject(fetched_sbj)

    SESSION_CNT = dict(
        Breast=4,
        Sarcoma=3
    )

    def test_reseed(self):
        subjects = seed.seed()
        expected = set(str(sbj) for sbj in self._subjects)
        actual = set(str(sbj) for sbj in subjects)
        assert_equal(actual, expected, "Reseed result is incorrect -"
                                       "\nexpected:\n%s\nfound:\n%s" %
                                       (expected, actual))

    def _validate_subject(self, subject):
        collections = ((coll.name for coll in seed.COLLECTIONS))
        assert_in(subject.collection, collections,
                  "Collection is invalid: %s" % subject.collection)
        self._validate_demographics(subject)
        self._validate_clincal_data(subject)
        self._validate_sessions(subject)

    def _validate_demographics(self, subject):
        assert_is_not_none(subject.gender, "%s is missing gender" % subject)

    def _validate_clincal_data(self, subject):
        # There are three treatments.
        self._validate_treatments(subject)
        # Validate the clinical encounters.
        self._validate_clinical_encounters(subject)

    def _validate_treatments(self, subject):
        # There are three treatments.
        treatments = subject.treatments
        assert_is_not_none(treatments, "%s has no treatments" % subject)
        assert_equal(len(treatments), 3,
                     "%s Subject %d treatments count is incorrect: %d" %
                     (subject.collection, subject.number, len(treatments)))
        # Breast has neoadjuvant drugs.
        if subject.collection == 'Breast':
            self._validate_breast_treatments(subject, treatments)

    def _validate_breast_treatments(self, subject, treatments):
        # Breast has neoadjuvant drugs.
        neo_rx = next(((trt for trt in treatments if trt.treatment_type == 'Neoadjuvant')),
                      None)
        assert_is_not_none(neo_rx, ("%s Subject %d is missing a neodjuvant" +
                                    " treatment") % (subject.collection, subject.number))
        dosages = neo_rx.dosages
        assert_equal(len(dosages), 2,
                     (("%s session %d neoadjuvant treatment dosage count is" +
                      " incorrect: %d") % (subject.collection, subject.number, len(dosages))))
        # Validate the agent type and dosage unit.
        for dosage in dosages:
            agent = dosage.agent
            assert_is_instance(agent, Drug,
                               "%s Subject %d neoadjuvant agent is not a drug" %
                               (subject.collection, subject.number))
            amount = dosage.amount
            assert_is_not_none(amount, ("%s Subject %d is missing a neodjuvant drug" +
                                      " dosage amount") % (subject.collection, subject.number))

    def _validate_clinical_encounters(self, subject):
        # There are two clinical encounters.
        cln_encs = list(subject.clinical_encounters)
        assert_is_not_none(cln_encs, "%s has no encounters" % subject)
        assert_equal(len(cln_encs), 2,
                     "%s Subject %d encounter count is incorrect: %d" %
                     (subject.collection, subject.number, len(cln_encs)))

        # Each encounter has a subject weight.
        for enc in cln_encs:
            assert_is_not_none(enc.weight, "%s encounter %s is missing the"
                                           " subject weight" % (subject, enc))
            assert_is_instance(enc.weight, int,
                               "%s encounter %s weight type is incorrect: %s" %
                               (subject, enc, enc.weight.__class__))

        # There is a biopsy with a pathology report.
        biopsy = next((enc for enc in cln_encs if isinstance(enc, Biopsy)),
                      None)
        assert_is_not_none(biopsy, "%s Subject %d is missing a biopsy" %
                                   (subject.collection, subject.number))
        self._validate_pathology(subject, biopsy.pathology)
        # Breast pre-neoadjuvant biopsy does not have a RCB.
        if subject.collection == 'Breast':
            tumor_pathology = biopsy.pathology.tumors[0]
            assert_is_none(tumor_pathology.rcb,
                           "%s biopsy pathology report incorrectly has a RCB"
                           " status" % subject)

        # There is a surgery with a pathology report.
        surgery = next((enc for enc in cln_encs if isinstance(enc, Surgery)),
                       None)
        assert_is_not_none(surgery, "%s Subject %d is missing a surgery" %
                                     (subject.collection, subject.number))
        assert_is_not_none(surgery.pathology,
                     "%s surgery is missing a pathology report" % subject)
        self._validate_pathology(subject, surgery.pathology)
        # Surgery has a RCB.
        if subject.collection == 'Breast':
            tumor_pathology = surgery.pathology.tumors[0]
            assert_is_not_none(tumor_pathology.rcb,
                               "%s surgery pathology report is missing a"
                               " RCB status" % subject)

    def _validate_pathology(self, subject, pathology_report):
        assert_is_not_none(pathology_report, "%s is missing a pathology"
                                             " report" % subject)
        assert_false(len(pathology_report.tumors) == 0,
                     "%s has no pathology tumor report")
 
        for tumor_pathology in pathology_report.tumors:
            self._validate_tnm(subject, tumor_pathology.tnm)
            # The tumor-specific tests.
            if subject.collection == 'Breast':
                self._validate_breast_pathology(subject, tumor_pathology)
            elif subject.collection == 'Sarcoma':
                self._validate_sarcoma_pathology(subject, tumor_pathology)

    def _validate_tnm(self, subject, tnm):
        assert_is_not_none(tnm, "%s is missing a TNM" % subject)
        assert_is_not_none(tnm.tumor_type,
                           "%s TNM is missing the tumor type" % subject)
        assert_is_not_none(tnm.grade,
                           "%s TNM is missing the grade" % subject)
        assert_is_not_none(tnm.size,
                           "%s TNM is missing the composite size object" %
                           subject)
        assert_is_not_none(tnm.size.tumor_size,
                           "%s TNM is missing the size score" % subject)
        assert_is_not_none(tnm.lymph_status,
                           "%s TNM is missing the lymph status" % subject)
        assert_is_not_none(tnm.lymphatic_vessel_invasion,
                           "%s TNM is missing the lymphati vessel invasion"
                           % subject)
        assert_is_not_none(tnm.metastasis,
                           "%s TNM is missing the metastasis" % subject)

    def _validate_breast_pathology(self, subject, pathology):
        estrogen = next((hr for hr in pathology.hormone_receptors
                         if hr.hormone == 'estrogen'),
                        None)
        assert_is_not_none(estrogen, "%s pathology report is missing"
                                     " an estrogen status" % subject)
        progesterone = next((hr for hr in pathology.hormone_receptors
                             if hr.hormone == 'progesterone'),
                            None)
        assert_is_not_none(progesterone, "%s pathology report is missing a"
                                         " progesterone status" % subject)
        assert_is_not_none(pathology.genetic_expression,
                           "%s pathology report is missing a genetic"
                           " expression status" % subject)
        assert_is_not_none(pathology.genetic_expression.her2_neu_ihc,
                           "%s pathology report is missing a"
                           " HER2 NEU IHC status" % subject)
        assert_is_not_none(pathology.genetic_expression.her2_neu_fish,
                           "%s pathology report is missing a"
                           " HER2 NEU FISH status" % subject)
        assert_is_not_none(pathology.genetic_expression.ki67,
                           "%s pathology report is missing a"
                           " Ki67 status" % subject)
        # The first breast subject has value overrides.
        if subject.number == 1:
            assert_true(estrogen.positive, "The first Breast subject is not"
                                           " estrogen-receptor-positive")
            assert_equal(pathology.tnm.lymph_status, 0,
                         "The first Breast subject lymph status is incorrect")
        # A subject who is estrogen-receptor-positive and has no lymph nodes
        # has a normalized assay.
        if estrogen.positive and not pathology.tnm.lymph_status:
            assay = pathology.genetic_expression.normalized_assay
            assert_is_not_none(assay, "%s pathology report with HER2"
                                      " positive and no lymph nodes is missing"
                                      " a normalized assay" % subject)
            assert_is_not_none(assay.gstm1, "%s pathology report"
                                            " normalized assay is missing"
                                            " a GSTM1 result" % subject)
            assert_is_not_none(assay.cd68, "%s pathology report"
                                           " normalized assay is missing"
                                           " a CD68 result" % subject)
            assert_is_not_none(assay.bag1, "%s pathology report"
                                           " normalized assay is missing"
                                           " a BAG1 result" % subject)
            assert_is_not_none(assay.her2, "%s pathology report"
                                           " normalized assay is missing"
                                           " the HER2 group" % subject)
            assert_is_not_none(assay.estrogen, "%s pathology report"
                                               " normalized assay is missing"
                                               " the estrogen group" % subject)
            assert_is_not_none(assay.proliferation, "%s pathology report"
                                                    " normalized assay is"
                                                    " missing the proliferation"
                                                    " group" % subject)
            assert_is_not_none(assay.invasion, "%s pathology report"
                                               " normalized assay is missing"
                                               " the invasion group" % subject)

    def _validate_sarcoma_pathology(self, subject, pathology):
        assert_is_not_none(pathology.location,
                           "%s pathology report is missing a tumor location" % subject)

    def _validate_sessions(self, subject):
        sessions = list(subject.sessions)
        assert_is_not_none(sessions, "%s has no sessions" % subject)
        session_cnt = TestSeed.SESSION_CNT[subject.collection]
        assert_equal(len(sessions), session_cnt, "%s session count is incorrect: %d" %
                                  (subject, len(sessions)))
        for i, session in enumerate(sessions):
            # Set a session number for reporting.
            session.number = i + 1
            self._validate_session(subject, session)

    def _validate_session(self, subject, session):
        assert_is_not_none(session.date,
                           "%s session %d is missing the acquisition date" %
                           (subject, session.number))
        assert_is_instance(session.date, datetime,
                           "%s session %d acquisition date type is incorrect: %s" %
                           (subject, session.number, session.date.__class__))
        self._validate_modeling(subject, session)
        self._validate_session_detail(subject, session)

    def _validate_modeling(self, subject, session):
        # The registration is modeled.
        assert_equal(len(session.modelings), 1,
                     "%s session %d modeling length is incorrect: %d" %
                     (subject, session.number, len(session.modelings)))
        modeling = session.modelings[0]
        assert_is_not_none(modeling.resource,
                           "%s session %d is missing the modeling resource" %
                           (subject, session.number))
        assert_is_not_none(modeling.protocol,
                           "%s session %d modeling %s is missing the protocol" %
                           (subject, session.number, modeling.resource))
        assert_is_not_none(modeling.source,
                           "%s session %d modeling %s is missing the source" %
                           (subject, session.number, modeling.resource))

        # Validate the modeling result.
        for param in MODELING_RESULT_PARAMS:
            value = modeling.result[param]
            assert_is_not_none(value,
                               "%s Subject %d modeling %s is missing a %s parameter" %
                               (subject.collection, subject.number, modeling.resource, param))
            assert_is_not_none(value.image,
                               "%s Subject %d modeling %s is missing a %s image" %
                               (subject.collection, subject.number, modeling.resource, param))
            metadata = value.image.metadata
            assert_is_not_none(metadata,
                               "%s Subject %d modeling %s is missing %s metadata" %
                               (subject.collection, subject.number, modeling.resource, param))
            avg = metadata.get('average_intensity')
            assert_is_not_none(avg,
                               "%s Subject %d modeling %s is missing %s intensity" %
                               (subject.collection, subject.number, modeling.resource, param))

        # The delta Ktrans result has an overlay.
        label_map = modeling.result['delta_k_trans'].label_map
        assert_is_not_none(label_map,
                           "%s Subject %d modeling is missing a label_map" %
                           (subject.collection, subject.number))
        assert_is_not_none(label_map.name,
                           "%s Subject %d modeling label map is missing a file name" %
                           (subject.collection, subject.number))
        assert_is_not_none(label_map.color_table,
                           "%s Subject %d modeling   label map is missing a color table" %
                           (subject.collection, subject.number))

    def _validate_session_detail(self, subject, session):
        assert_is_not_none(session.detail, "%s session %d is missing detail" %
                                           (subject, session.number))
        # Validate the scans.
        scans = session.detail.scans
        assert_equal(len(scans), 2, "%s session %d scan count is incorrect: %d" %
                                    (subject, session.number, len(scans)))

        # The T1 scan.
        scan = scans[0]
        coll = seed.collection_for(subject.collection)
        expected_volume_cnt = coll.options.volume_count
        assert_equal(len(scan.volumes.images), expected_volume_cnt,
                     "%s session %d scan %d volumes count is incorrect: %d" %
                     (subject, session.number, scan.number, len(scan.volumes.images)))
        for i, image in enumerate(scan.volumes.images):
            assert_is_not_none(image.metadata,
                               "%s session %d scan %d volume %d is missing metadata" %
                               (subject, session.number, scan.number, i + 1))
            avg = image.metadata.get('average_intensity')
            assert_is_not_none(avg,
                               "%s session %d scan %d volume %d is missing an intensity" %
                               (subject, session.number, scan.number, i + 1))
            # Verify that intensities are floats.
            assert_true(isinstance(avg, float),
                        "%s session %d scan %d volume %d intensity type is"
                        " incorrect for value %s: %s" %
                        (subject, session.number, scan.number, i + 1, avg, avg.__class__))

        # Validate the registration.
        regs = scan.registrations
        assert_equal(len(regs), 1, "%s session %d scan %d registration count"
                                    " is incorrect: %d" %
                                    (subject, session.number, scan.number, len(regs)))
        for reg in regs:
            for i, image in enumerate(reg.volumes.images):
                assert_is_not_none(image.metadata,
                                   "%s session %d scan %d registration %s volume %d"
                                   " is missing metadata" %
                                   (subject, session.number, scan.number,
                                    reg.volumes.name, i + 1))
                avg = image.metadata.get('average_intensity')
                assert_is_not_none(avg,
                                   "%s session %d scan %d registration %s volume %d"
                                   " is missing an intensity" %
                                   (subject, session.number, scan.number,
                                    reg.volumes.name, i + 1))
                assert_true(isinstance(avg, float),
                            "%s session %d scan %d registration %s volume %d intensity"
                            " type is incorrect for value %s: %s" %
                            (subject, session.number, scan.number, reg.volumes.name,
                             i + 1, avg, avg.__class__))

        # The T2 scan has one volume without an intensity value.
        scan = scans[1]
        assert_equal(len(scan.volumes.images), 1,
                     "%s session %d scan %d volumes count is incorrect: %d" %
                     (subject, session.number, scan.number, len(scan.volumes.images)))
        image = scan.volumes.images[0]
        assert_true(not image.metadata,
                       "%s session %d scan %d volume incorrectly has metadata" %
                       (subject, session.number, scan.number))


if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)

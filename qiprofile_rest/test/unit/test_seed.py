from nose.tools import (assert_is_none, assert_is_instance, assert_in,
                        assert_is_not_none, assert_true, assert_equal)
from datetime import datetime
from mongoengine import connect
from mongoengine.connection import get_db
from qiprofile_rest.models import Subject
from qiprofile_rest.test.helpers import seed

class TestSeed(object):
    """
    This TestSeed class tests the seed helper utility.

    Note: this test drops the ``qiprofile-test`` Mongo database
    at the beginning and end of execution.
    """
    def setup(self):
        connect(db='qiprofile_test')
        self.db = get_db()
        self.db.connection.drop_database('qiprofile_test')
        self._subjects = seed.seed()

    def tearDown(self):
        self.db.connection.drop_database('qiprofile_test')

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
 
    def _validate_subject(self, subject):
        assert_in(subject.collection, ['Breast', 'Sarcoma'],
                  "Collection is invalid: %s" % subject.collection)
        assert_is_not_none(subject.detail, "%s is missing detail" % subject)
        assert_is_not_none(subject.detail.sessions, "%s has no sessions" % subject)
        sessions = subject.detail.sessions
        session_cnt = TestSeed.SESSION_CNT[subject.collection]
        assert_equal(len(sessions), session_cnt, "%s session count is incorrect: %d" %
                                  (subject, len(sessions)))
        for session in sessions:
            self._validate_session(subject, session)

        treatments = subject.detail.treatments
        assert_equal(len(treatments), 3,
                     "%s session %d treatments count is incorrect: %d" %
                     (subject, session.number, len(treatments)))

        encounters = subject.detail.encounters
        assert_equal(len(encounters), 3,
                     "%s session %d encounter count is incorrect: %d" %
                     (subject, session.number, len(encounters)))
        biopsy = next((enc for enc in encounters if enc.encounter_type == 'Biopsy'),
                      None)
        assert_is_not_none(biopsy, "%s session %d is missing a biopsy" %
                                   (subject, session.number))
        assert_equal(len(biopsy.outcomes), 1, "%s biopsy outcomes size is"
                                              " incorrect" % subject)
        path = biopsy.outcomes[0]
        assert_is_not_none(path.tnm, "%s biopsy pathology report is missing"
                                     " a TNM" % subject)
        surgery = next((enc for enc in encounters if enc.encounter_type == 'Surgery'),
                      None)
        assert_is_not_none(surgery, "%s session %d is missing a surgery" %
                                     (subject, session.number))
        assert_equal(len(surgery.outcomes), 0,
                     "%s surgery incorrectly has an outcome" % subject)
        post_trt = next((enc for enc in encounters if enc.encounter_type == 'Assessment'),
                      None)
        assert_is_not_none(post_trt, "%s session %d is missing an assessment" %
                                     (subject, session.number))
        assert_equal(len(post_trt.outcomes), 1,
                     "%s post-treatment assessment outcomes size is incorrect" % subject)

    def _validate_session(self, subject, session):
        assert_is_not_none(session.acquisition_date,
                           "%s session %d is missing an acquisition date" %
                           (subject, session.number))
        assert_is_instance(session.acquisition_date, datetime,
                           "%s session %d acquisition date type is incorrect: %s" %
                           (subject, session.number, session.acquisition_date.__class__))
        assert_is_not_none(session.modeling, "%s session %d is missing modeling" %
                                          (subject, session.number))
        assert_is_not_none(session.detail, "%s session %d is missing detail" %
                                        (subject, session.number))
        assert_is_not_none(session.detail.scan, "%s session %d is missing scans" %
                                             (subject, session.number))

        scan_intensity = session.detail.scan.intensity
        assert_is_not_none(scan_intensity, "%s session %d scan is missing an"
                                           " intensity" % (subject, session.number))

        assert_true(not not session.detail.registrations,
               "%s session %d registration is missing a registration" %
               (subject, session.number))
        reg = session.detail.registrations[0]
        assert_equal(reg.name, "reg_%02d" % session.number,
                     "%s session %d registration name incorrect: %s" %
                     (subject, session.number, reg.name))
        assert_equal(reg.parameters, seed.REG_PARAMS,
                     "%s session %s %s parameters incorrect: %s" %
                     (subject, session.number, reg.name, reg.parameters))

        reg_intensity = reg.intensity
        assert_is_not_none(reg.intensity,
                           "%s session %d registration is missing an intensity" %
                            (subject, session.number))
        # Verify that decimals are decoded as numbers.
        for value in reg_intensity.intensities:
            assert_true(isinstance(value, float),
                        "Float field type is incorrect for value %s: %s" %
                        (value, value.__class__))


if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)

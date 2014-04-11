from nose.tools import (assert_is_none, assert_is_instance,
                        assert_is_not_none, assert_true, assert_equal)
from datetime import datetime
from qiprofile_rest.models import Subject
from qiprofile_rest.test.helpers import seed

class TestSerializers(object):
    def setup(self):
        self._subjects = seed.seed()
        
    def test_serialization(self):
        for saved_sbj in self._subjects:
            query = dict(project=saved_sbj.project,
                         collection=saved_sbj.collection,
                         number=saved_sbj.number)
            fetched_sbj = Subject.objects.get(**query)
            self._validate_subject(fetched_sbj)

    def _validate_subject(self, subject):
        assert_is_not_none(subject.detail, "%s is missing detail" % subject)
        assert_is_not_none(subject.detail.sessions, "%s has no sessions" % subject)
        sessions = subject.detail.sessions
        assert_equal(len(sessions), 4, "%s session count is incorrect: %d" %
                                  (subject, len(sessions)))
        for session in sessions:
            self._validate_session(subject, session)
        
        encounters = subject.detail.encounters
        assert_equal(len(encounters), 2,
                     "%s session %d encounter count is incorrect: %d" %
                     (subject, session.number, len(encounters)))
        biopsy = next((enc for enc in encounters if enc.encounter_type == 'Biopsy'),
                      None)
        assert_is_not_none(biopsy, "%s session %d is missing a biopsy" %
                                   (subject, session.number))
        assert_is_not_none(biopsy.id, "%s session %d biopsy is missing an id" %
                                      (subject, session.number))
        path = biopsy.outcome
        assert_is_not_none(path, "%s biopsy is missing a pathology report" %
                                 subject)
        assert_is_not_none(biopsy.id, "%s biopsy pathology report is missing"
                                      " an id" % subject)
        # Uncomment to print the biopsy result.
        # print "%s %s TNM: %s Estrogen: %d" % (subject, biopsy.encounter_type,
        #                                       path.tnm.size, path.estrogen.quick_score)
            
    def _validate_session(self, subject, session):
        assert_is_not_none(session.id, "%s session %d is missing an id" %
                                    (subject, session.number))
        assert_is_not_none(session.acquisition_date,
                           "%s session %d is missing an acquisition date" %
                           (subject, session.number))
        assert_is_instance(session.acquisition_date, datetime,
                           "%s session %d acquisition date type is incorrect: %s" %
                           (subject, session.number, session.acquisition_date.__class__))
        assert_is_not_none(session.modeling, "%s session %d is missing modeling" %
                                          (subject, session.number))
        assert_is_not_none(session.modeling.id, "%s session %d modeling is missing an id" %
                                          (subject, session.number))
        # Uncomment to print the modeling parameters.
        #mdl = session.modeling
        #print ("%s Session %d %f %f %f" % 
        #        (subject, session.number, mdl.delta_k_trans, mdl.v_e, mdl.tau_i))
        
        assert_is_not_none(session.detail, "%s session %d is missing detail" %
                                        (subject, session.number))
        assert_is_not_none(session.detail.scan, "%s session %d is missing scans" %
                                             (subject, session.number))
        assert_is_not_none(session.detail.scan.id, "%s session %d scan is missing an id"
                                                " an id" % (subject, session.number))
                    
        scan_intensity = session.detail.scan.intensity
        assert_is_not_none(scan_intensity, "%s session %d scan is missing an"
                                           " intensity" % (subject, session.number))
        assert_is_none(scan_intensity.id, "%s session %d scan intensity incorrectly"
                                          " has an id" % (subject, session.number))
        # Uncomment to print the scan intensity values.
        # print ("%s Session %d scan intensities:" % (subject, session.number))
        # print map(float, scan_intensity.intensities)
        assert_true(not not session.detail.reconstructions,
               "%s session %d registration is missing a registration" %
               (subject, session.number))
        reg = session.detail.reconstructions[0]
        assert_is_not_none(reg.id, "%s session %d registration is missing"
                                   " an id" % (subject, session.number))
        reg_intensity = reg.intensity
        assert_is_not_none(reg.intensity,
                           "%s session %d registration is missing an intensity" %
                            (subject, session.number))
        assert_is_none(reg.intensity.id,
                       "%s session %d registration intensity incorrectly"
                       " has an id" % (subject, session.number))
        # Verify that decimals are decoded as numbers.
        for value in reg_intensity.intensities:
            assert_true(isinstance(value, float),
                        "Float field type is incorrect for value %s: %s" %
                        (value, value.__class__))
        # Uncomment to print the registration intensity values.
        # print ("%s Session %d registration intensities:" % (subject, session.number))
        # print map(float, reg_intensity.intensities)


if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)

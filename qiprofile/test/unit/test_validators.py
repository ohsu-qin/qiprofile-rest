from nose.tools import assert_is_none, assert_raises
from django.core.exceptions import ValidationError
from qiprofile import validators

class TestValidators(object):
    def test_tnm_size_validator(self):
        for value in ['T1', 'Tx', 'cT4', 'T1b', 'cT2a']:
            assert_is_none(validators.validate_tnm_size(value),
                           "Valid value not validated: %s" % value)
        
        for value in ['Tz', 'T', '4', 'cT4d']:
            assert_raises(ValidationError, validators.validate_tnm_size, value)


if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)

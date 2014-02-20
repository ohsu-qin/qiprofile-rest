from nose.tools import assert_equal
from qiprofile import choices

class TestChoices(object):
    def test_arabic_range_choices(self):
        expected = [('1', 1), ('2', 2), ('3', 3)]
        actual = choices.range_choices(1, 4)
        assert_equal(actual, expected)

    def test_roman_range_choices(self):
        expected = [('I', 1), ('II', 2), ('III', 3), ('IV', 4)]
        actual = choices.range_choices(1, 5, True)
        assert_equal(actual, expected)


if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)

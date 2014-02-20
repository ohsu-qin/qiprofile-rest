

POS_NEG_CHOICES = [('Positive', True), ('Negative', False)]
"""The Boolean choices for Positive or Negative status."""

RACE_CHOICES = [('White', 'White'),
                ('Black' , 'Black or African American'),
                ('Asian', 'Asian'),
                ('AIAN' , 'American Indian or Alaska Native'),
                ('NHOPI' , 'Native Hawaiian or Other Pacific Islander')]
"""The standard FDA race categories."""

ETHNICITY_CHOICES = [('Hispanic' , 'Hispanic or Latino'),
                     ('Non-Hispanic' , 'Not Hispanic or Latino')]
"""The standard FDA ethnicity categories."""


def max_length(choices):
    """
    Returns the size of the longest choice.
    
    :param: the available choice strings
    :return: the maximum length
    """
    return max((len(c) for c in choices))


def range_choices(start, stop, roman=False):
    """
    Returns the choices for the given exclusive range bounds.
     
    Example:

    >>> from qiprofile import choices
    >>> choices.range_choices(1, 4)
    [('1', 1), ('2', 2), ('3', 3)]

    >>> from qiprofile import choices
    >>> choices.range_choices(1, 5, roman=True)
    [('I', 1), ('II', 2), ('III', 3), ('IV', 4)]
    
    :param start: the first value in the range
    :param stop: one greater than the last value in the range
    :param roman: flag indicating whether the display value
        is a roman numeral
    :return: the {value: label} choices dictionary
    :raise ValueError: if the *roman* flag is set and start
        is less than one or stop is greater than five
    """
    if roman:
        formatter = _roman
    else:
        formatter = str
    return [(formatter(v), v) for v in range(start, stop)]


def _roman(n):
    """
    :param n: the input integer
    :return the roman numeral
    :raise ValueError: if the input integer is not a
        positive integer less than five
    """
    if n not in range(1, 5):
        raise ValueError("The roman numeral converter is not supported for"
                         " the value %d" % n)
    if n == 4:
        return 'IV'
    else:
        return 'I' * n

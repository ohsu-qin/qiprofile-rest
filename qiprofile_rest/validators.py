import re
from django.core.validators import *
from django.core.exceptions import ValidationError


def range_validators(start, stop):
    """
    Returns the validators for the given exclusive range bounds.

    :param start: the first value in the range
    :param stop: one greater than the last value in the range
    :return: the [min, max] validators list
    """
    return [MinValueValidator(0), MaxValueValidator(stop - 1)]


## TNM validation. ##

TNM_SIZE_PAT = """
    ^(c|p|y|r|a|u)? # The prefix modifier
    T               # The size designator
    (x |            # Tumor cannot be evaluated
     is |           # Carcinoma in situ
     ((0|1|2|3|4)   # The size
      (a|b|c)?      # The suffix modifier
     )
    )$
"""

TNM_SIZE_REGEX = re.compile(TNM_SIZE_PAT, re.VERBOSE)

validate_tnm_size = RegexValidator(TNM_SIZE_REGEX, "Invalid TNM size")

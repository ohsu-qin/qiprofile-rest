"""
The Imaging Profile Mongodb data model.

This model can be normalized to a relational database back-end as
follows:

* Create the Project and Collection classes with a *name* field.

* Reference the Project and Collection from Subject.

* Pull SubjectDetail into Subject.

* Replace each embedded field with a foreign key.

* Replace each list field with a one-to-many relationship or
  MultiSelectField.
"""

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from djangotoolbox.fields import (ListField, EmbeddedModelField)
from . import (choices, validators)


class Subject(models.Model):
    """
    The QIN patient.
    """

    project = models.CharField(max_length=200, default='QIN')
    collection = models.CharField(max_length=200)
    number = models.SmallIntegerField()
    detail = models.ForeignKey('SubjectDetail', null=True, blank=True)

    def __str__(self):
        return ("%s %s Subject %d" %
                (self.project, self.collection, self.number))


class SubjectDetail(models.Model):
    """
    The QIN patient detail aggregate. The Mongodb quiprofile_subject_detail
    document embeds the subject sessions and outcomes.
    """

    birth_date = models.DateTimeField(null=True)
    race = ListField(
        models.CharField(max_length=choices.max_length(choices.RACE_CHOICES),
                         choices=choices.RACE_CHOICES),
        blank=True)
    ethnicity = models.CharField(
        max_length=choices.max_length(choices.ETHNICITY_CHOICES),
        choices=choices.ETHNICITY_CHOICES, null=True, blank=True)
    sessions = ListField(EmbeddedModelField('Session'), blank=True)
    encounters = ListField(EmbeddedModelField('Encounter'), blank=True)


class Session(models.Model):
    """The QIN visit MR Session."""

    number = models.IntegerField()
    acquisition_date = models.DateTimeField()
    reg_images = ListField(models.FilePathField(max_length=255))
    bolus_arrival_index = models.SmallIntegerField()
    modeling = ListField(EmbeddedModelField('Modeling'))

    def __str__(self):
        return "%s Visit %d" % (subject, self.number)


## Imaging metrics ##

class Modeling(models.Model):
    """The QIN pharmicokinetic modeling result."""

    name = models.CharField(max_length=200)
    delta_k_trans = models.DecimalField(max_digits=5, decimal_places=4)
    v_e = models.DecimalField(max_digits=5, decimal_places=4)
    tau_i = models.DecimalField(max_digits=5, decimal_places=4)

    def __str__(self):
        return "%s modeling" % session


## Patient encounter. ##

class Encounter(models.Model):
    """The QIN patient clinical encounter, e.g. biopsy."""
    
    TYPE_CHOICES = [(v, v) for v in ('Biopsy', 'Surgery', 'Other')]
    
    encounter_type = models.CharField(
        max_length=choices.max_length(TYPE_CHOICES),
        choices=TYPE_CHOICES)
    
    date = models.DateTimeField()
    
    outcomes = ListField(EmbeddedModelField('Outcome'))


## Clinical outcomes. ##

class Outcome(models.Model):
    """The QIN patient clinical outcome."""

    class Meta:
        abstract = True


class Pathology(Outcome):
    """The patient pathology summary."""

    class Meta:
        abstract = True

    tnm = EmbeddedModelField('TNM')


class BreastPathology(Pathology):
    """The QIN breast patient pathology summary."""

    HER2_NEU_IHC_CHOICES = choices.range_choices(0, 4)

    KI_67_VALIDATORS = validators.range_validators(0, 101)

    grade = EmbeddedModelField('NottinghamGrade')
    estrogen = EmbeddedModelField('HormoneReceptorStatus')
    progestrogen = EmbeddedModelField('HormoneReceptorStatus')
    her2_neu_ihc = models.SmallIntegerField(choices=HER2_NEU_IHC_CHOICES)
    her2_neu_fish = models.SmallIntegerField(choices=choices.POS_NEG_CHOICES)
    ki_67 = models.SmallIntegerField(validators=KI_67_VALIDATORS)


class SarcomaPathology(Pathology):
    """The QIN sarcoma patient pathology summary."""

    HISTOLOGY_CHOICES = [
        (v, v) for v in ('Fibrosarcoma', 'Leiomyosarcoma', 'Liposarcoma',
                         'MFH', 'MPNT', 'Synovial', 'Other')
    ]

    site = models.CharField(max_length=200)
    histology = models.CharField(
        max_length=choices.max_length(HISTOLOGY_CHOICES),
        choices=HISTOLOGY_CHOICES)


## Clinical metrics ##

class TNM(models.Model):
    """The TNM tumor staging."""

    GRADE_CHOICES = choices.range_choices(1, 4)

    SIZE_VALIDATOR = validators.validate_tnm_size
    
    # TODO - add other validators

    size = models.CharField(max_length=4, validators=[SIZE_VALIDATOR])
    lymph_status = models.CharField(max_length=4)
    metastasis = models.CharField(max_length=4)
    grade = models.SmallIntegerField(choices=GRADE_CHOICES)


class NottinghamGrade(models.Model):
    """The Nottingham tumor grade."""

    COMPONENT_CHOICES = choices.range_choices(1, 4)

    tubular_formation = models.SmallIntegerField(choices=COMPONENT_CHOICES)
    nuclear_pleomorphism = models.SmallIntegerField(choices=COMPONENT_CHOICES)
    mitotic_count = models.SmallIntegerField(choices=COMPONENT_CHOICES)


class HormoneReceptorStatus(models.Model):
    """The QIN patient estrogen/progesterone hormone receptor status."""

    SCORE_CHOICES = choices.range_choices(0, 9)

    INTENSITY_VALIDATORS = validators.range_validators(0, 101)

    positive = models.BooleanField(choices=choices.POS_NEG_CHOICES)
    quick_score = models.SmallIntegerField(choices=SCORE_CHOICES)
    intensity = models.SmallIntegerField(validators=INTENSITY_VALIDATORS)

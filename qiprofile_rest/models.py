"""
The Imaging Profile Mongodb data model.

This model can be normalized to a relational database back-end as
follows:

* Pull SubjectDetail into Subject.

* Replace each embedded field with a foreign key.

* Replace each list field with a one-to-many relationship or
  MultiSelectField.

* Replace each dictionary field with a one-to-many reference to a
  property name/value table.

* Remove the ``managed = False`` setting for embedded classes.

* Remove the ``Outcome`` abstract class ``outcome_type`` field.

* Change the Float fields to Decimal fields.

:Note: each list embedded model field argument must be a class
  rather than a string to work around the following ``djangotoolbox``
  bug:

  * djangotoolbox definition of an abstract embedded field raises
    an exception
"""

from __future__ import unicode_literals
import re
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from djangotoolbox.fields import (ListField, DictField, EmbeddedModelField)
from bson.objectid import ObjectId
from . import (choices, validators)


#### Serialization work-around ####

from rest_framework import renderers
from rest_framework.utils import encoders

class EmbeddedMixin(object):
    """
    Mixin which marks an embedded model. This mixin is used with the
    custom encoder below to work around the following Django Mongo
    Engine djangotoolbox bug:
    
    * A field defined as a list of embedded models fails in
      django-rest-framework serialization.
    """
    pass


class JSONEncoder(encoders.JSONEncoder):
    """
    This class operates in conjunction with :class:`EmbeddedMixin`
    to work around a Django Mongo Engine djangotoolbox bug.
    """
    
    def default(self, o):
        """Provides a default enocoding for an embedded object."""
        if isinstance(o, EmbeddedMixin):
            # Encode the content, excluding the djangotoolbox
            # _model and _module attributes, which are only used
            # internally to restore the object.
            o = dict((item for item in o.__dict__.iteritems()
                      if not item[0].startswith('_')))

        return super(JSONEncoder, self).default(o)


renderers.JSONRenderer.encoder_class = JSONEncoder

#### End of serialization work-around ####


class Idable(object):
    """
    Mixin which marks an embedded model with auto-generated id.
    """
    pass


class EmbeddedModelFieldOverride(EmbeddedModelField):
    """
    This class extends ``EmbeddedModelField`` to autogenerate an id
    on object create if the embedded object is an Idable.
    """
    def get_db_prep_save(self, embedded_instance, *args, **kwargs):
        field_values = super(EmbeddedModelFieldOverride, self).get_db_prep_save(
            embedded_instance, *args, **kwargs
        )
        if isinstance(embedded_instance, Idable):
            pk_field = next((field for field in embedded_instance._meta.fields
                             if field.primary_key), None)
            if pk_field and not getattr(embedded_instance, pk_field.attname):
                oid = ObjectId()
                setattr(embedded_instance, pk_field.attname, oid)
                field_values[pk_field] = oid
        
        return field_values


class User(models.Model):
    """
    The application user.
    """

    class Meta:
        db_table = 'qiprofile_user'

    email = models.CharField(max_length=200)
    first_time = models.BooleanField(default=True)

    def __str__(self):
        return self.email


class Subject(models.Model):
    """
    The patient.
    """

    class Meta:
        db_table = 'qiprofile_subject'

    project = models.CharField(max_length=200, default='QIN')
    collection = models.CharField(max_length=200)
    number = models.SmallIntegerField()
    
    detail = models.OneToOneField('SubjectDetail', related_name='+')
    """Reference to the subject detail. The '+' related name
       prevents creation of a detail-to-subject foreign key field."""

    def delete(self):
        """Cascade delete this Subject."""
        if self.detail:
            self.detail.delete()
        super(Subject, self).delete()

    def __str__(self):
        return ("%s %s Subject %d" %
                (self.project, self.collection, self.number))


class SubjectDetail(models.Model):
    """
    The patient detail aggregate. The Mongodb quiprofile_subject_detail
    document embeds the subject sessions and outcomes.
    """

    class Meta:
        db_table = 'qiprofile_subject_detail'

    birth_date = models.DateTimeField(null=True)
    races = ListField(
        models.CharField(max_length=choices.max_length(choices.RACE_CHOICES),
                         choices=choices.RACE_CHOICES),
        blank=True)
    ethnicity = models.CharField(
        max_length=choices.max_length(choices.ETHNICITY_CHOICES),
        choices=choices.ETHNICITY_CHOICES, null=True, blank=True)
    sessions = ListField(EmbeddedModelFieldOverride('Session'), blank=True)
    encounters = ListField(EmbeddedModelFieldOverride('Encounter'), blank=True)

    def delete(self):
        """Cascade delete this SubjectDetail."""
        for sess in self.sessions:
            sess.delete()
        super(SubjectDetail, self).delete()


class Session(models.Model, EmbeddedMixin, Idable):
    """The MR session (*study* in DICOM terminology)."""

    class Meta:
        managed = False

    number = models.IntegerField()
    acquisition_date = models.DateTimeField()
    modeling = EmbeddedModelFieldOverride('Modeling')
    
    detail = models.OneToOneField('SessionDetail', related_name='+')
    """Reference to the session detail. The '+' related name
       prevents creation of a detail-to-session foreign key field."""

    def delete(self):
        """Cascade delete this Session."""
        if self.detail:
            self.detail.delete()
        # Don't call superclass delete, since Session is embedded.

    def __str__(self):
        return "Session %d" % self.number


class SessionDetail(models.Model):
    """The MR session detailed content."""

    class Meta:
        db_table = 'qiprofile_session_detail'

    bolus_arrival_index = models.SmallIntegerField()
    series = ListField(EmbeddedModelFieldOverride('Series'))
    scan = EmbeddedModelFieldOverride('Scan')
    registrations = ListField(EmbeddedModelFieldOverride('Registration'))


class Series(models.Model, EmbeddedMixin, Idable):
    """The MR series."""

    class Meta:
        managed = False

    number = models.SmallIntegerField()


class Modeling(models.Model, EmbeddedMixin, Idable):
    """The QIN pharmicokinetic modeling result."""

    class Meta:
        managed = False

    name = models.CharField(max_length=200)
    fxl_k_trans = models.FloatField()
    fxr_k_trans = models.FloatField()
    v_e = models.FloatField()
    tau_i = models.FloatField()

    def __str__(self):
        return "Modeling %s" % self.name


class ImageContainer(models.Model, EmbeddedMixin, Idable):
    """The patient scan or registration."""

    class Meta:
        abstract = True

    files = ListField(models.CharField(max_length=200))
    
    # TODO - is there a use case for several intensity measures
    # per container?
    intensity = EmbeddedModelFieldOverride('Intensity')


class Scan(ImageContainer):
    """The patient image scan."""

    class Meta:
        managed = False


class Registration(ImageContainer):
    """The patient image registration that results from processing
    the image scan."""

    class Meta:
        managed = False

    name = models.CharField(max_length=200)
    """The resource name, e.g. ``reg_k3RtZ``"""
    
    parameters = DictField()

    def __str__(self):
        return "Registration %s" % self.name


class Intensity(models.Model, EmbeddedMixin):
    """The image signal intensities for a given probe."""

    class Meta:
        managed = False

    probe = EmbeddedModelFieldOverride('Probe', null=True, blank=True)
    
    intensities = ListField(models.FloatField())
    """The list of series intensities."""


class Probe(models.Model, EmbeddedMixin):
    """The image probe to conduct a measurement."""

    class Meta:
        managed = False

    description = models.CharField(max_length=200)
    """The short description, e.g. ``ROI centroid``"""
    
    location = ListField(models.FloatField())
    """The (x, y, z) probe coordinates"""

    def __str__(self):
        return "Probe %s at %s" % (self.description, tuple(self.location))


## Clinical outcomes. ##

class Outcome(models.Model, EmbeddedMixin):
    """The patient clinical outcome."""

    class Meta:
        abstract = True


## Patient encounter. ##

class Encounter(models.Model, EmbeddedMixin, Idable):
    """The patient clinical encounter, e.g. biopsy."""

    class Meta:
        managed = False
    
    TYPE_CHOICES = [(v, v) 
                    for v in ('Biopsy', 'Surgery', 'Assessment', 'Other')]
    
    encounter_type = models.CharField(
        max_length=choices.max_length(TYPE_CHOICES),
        choices=TYPE_CHOICES)
    
    date = models.DateTimeField()
    
    outcome = EmbeddedModelFieldOverride(Outcome)


class Pathology(Outcome):
    """The patient pathology summary."""

    class Meta:
        abstract = True

    tnm = EmbeddedModelFieldOverride('TNM')


class BreastPathology(Pathology):
    """The QIN breast patient pathology summary."""

    class Meta:
        managed = False

    HER2_NEU_IHC_CHOICES = choices.range_choices(0, 4)

    KI_67_VALIDATORS = validators.range_validators(0, 101)

    grade = EmbeddedModelFieldOverride('NottinghamGrade')
    estrogen = EmbeddedModelFieldOverride('HormoneReceptorStatus')
    progestrogen = EmbeddedModelFieldOverride('HormoneReceptorStatus')
    her2_neu_ihc = models.SmallIntegerField(choices=HER2_NEU_IHC_CHOICES)
    her2_neu_fish = models.BooleanField(choices=choices.POS_NEG_CHOICES)
    ki_67 = models.SmallIntegerField(validators=KI_67_VALIDATORS)


class SarcomaPathology(Pathology):
    """The QIN sarcoma patient pathology summary."""

    class Meta:
        managed = False

    HISTOLOGY_CHOICES = [
        (v, v) for v in ('Fibrosarcoma', 'Leiomyosarcoma', 'Liposarcoma',
                         'MFH', 'MPNT', 'Synovial', 'Other')
    ]

    site = models.CharField(max_length=200)
    histology = models.CharField(
        max_length=choices.max_length(HISTOLOGY_CHOICES),
        choices=HISTOLOGY_CHOICES)


## Clinical metrics ##

class TNM(Outcome):
    """The TNM tumor staging."""

    class Meta:
        managed = False

    LYMPH_CHOICES = choices.range_choices(0, 4)

    GRADE_CHOICES = choices.range_choices(1, 4)

    SIZE_VALIDATOR = validators.validate_tnm_size

    size = models.CharField(max_length=4, validators=[SIZE_VALIDATOR])
    lymph_status = models.SmallIntegerField(choices=LYMPH_CHOICES)
    metastasis = models.BooleanField(choices=choices.POS_NEG_CHOICES)
    grade = models.SmallIntegerField(choices=GRADE_CHOICES)


class NottinghamGrade(Outcome):
    """The Nottingham tumor grade."""

    class Meta:
        managed = False

    COMPONENT_CHOICES = choices.range_choices(1, 4)

    tubular_formation = models.SmallIntegerField(choices=COMPONENT_CHOICES)
    nuclear_pleomorphism = models.SmallIntegerField(choices=COMPONENT_CHOICES)
    mitotic_count = models.SmallIntegerField(choices=COMPONENT_CHOICES)


class HormoneReceptorStatus(Outcome):
    """The patient estrogen/progesterone hormone receptor status."""

    class Meta:
        managed = False

    SCORE_CHOICES = choices.range_choices(0, 9)

    INTENSITY_VALIDATORS = validators.range_validators(0, 101)

    positive = models.BooleanField(choices=choices.POS_NEG_CHOICES)
    quick_score = models.SmallIntegerField(choices=SCORE_CHOICES)
    intensity = models.SmallIntegerField(validators=INTENSITY_VALIDATORS)

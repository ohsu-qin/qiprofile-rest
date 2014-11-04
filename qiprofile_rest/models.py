"""
The qiprofile Mongodb data model.
"""

import re
import mongoengine
from mongoengine import (fields, signals, ValidationError)
from . import choices

class User(mongoengine.Document):
    """
    The application user.
    """

    meta = dict(collection='qiprofile_user')

    email = fields.StringField()
    first_time = fields.BooleanField(default=True)

    def __str__(self):
        return self.email


class Subject(mongoengine.Document):
    """
    The patient.
    """

    meta = dict(collection='qiprofile_subject')

    project = fields.StringField(default='QIN')

    collection = fields.StringField(required=True)

    number = fields.IntField(required=True)

    detail = fields.ReferenceField('SubjectDetail')

    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        """Cascade delete this Session's detail."""

        if self.detail:
            self.detail.delete()

    def __str__(self):
        return ("%s %s Subject %d" %
                (self.project, self.collection, self.number))

signals.pre_delete.connect(Subject.pre_delete, sender=Subject)


class SubjectDetail(mongoengine.Document):
    """
    The patient detail aggregate. The Mongodb quiprofile_subject_detail
    document embeds the subject sessions and outcomes.
    """

    meta = dict(collection='qiprofile_subject_detail')

    birth_date = fields.DateTimeField()

    races = fields.ListField(
        fields.StringField(max_length=choices.max_length(choices.RACE_CHOICES),
                           choices=choices.RACE_CHOICES))

    ethnicity = fields.StringField(
        max_length=choices.max_length(choices.ETHNICITY_CHOICES),
        choices=choices.ETHNICITY_CHOICES)

    sessions = fields.ListField(field=fields.EmbeddedDocumentField('Session'))

    treatments = fields.ListField(field=fields.EmbeddedDocumentField('Treatment'))

    encounters = fields.ListField(field=fields.EmbeddedDocumentField('Encounter'))

    def pre_delete(cls, sender, document, **kwargs):
        """Cascade delete this SubjectDetail's sessions."""

        for sess in self.sessions:
            sess.delete()


class Session(mongoengine.EmbeddedDocument):
    """The MR session (a.k.a. *study* in DICOM terminology)."""

    number = fields.IntField(required=True)

    acquisition_date = fields.DateTimeField()

    modeling = fields.ListField(field=mongoengine.EmbeddedDocumentField('Modeling'))

    detail = fields.ReferenceField('SessionDetail')

    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        """Cascade delete this Session's detail."""

        if self.detail:
            self.detail.delete()

signals.pre_delete.connect(Session.pre_delete, sender=Session)


class Series(mongoengine.EmbeddedDocument):
    """The MR series."""

    number = fields.IntField(required=True)


class Modeling(mongoengine.EmbeddedDocument):
    """The QIN pharmicokinetic modeling result."""

    name = fields.StringField(required=True)
    """The modeling resource name, e.g. ``pk_R3y9``."""

    source = fields.StringField(required=True)
    """
    The source image container id.
    This is not a ReferenceField to an ImageContainer,
    since ImageContainer is embedded in the SessionDetail.
    """

    fxl_k_trans = fields.EmbeddedDocumentField('ModelingParameter')

    fxr_k_trans = fields.EmbeddedDocumentField('ModelingParameter')

    delta_k_trans = fields.EmbeddedDocumentField('ModelingParameter')

    v_e = fields.EmbeddedDocumentField('ModelingParameter')

    tau_i = fields.EmbeddedDocumentField('ModelingParameter')

    parameters = fields.DictField()
    """The modeling execution input parameters."""

    def __str__(self):
        return "Modeling %s" % self.name


class ModelingParameter(mongoengine.EmbeddedDocument):
    """The discrete modeling result."""

    filename = fields.StringField(required=True)
    """The voxel-wise mapping file path relative to the web app root."""

    average = fields.FloatField(required=True)
    """The average parameter value over all voxels."""
    
    label_map = fields.EmbeddedDocumentField('LabelMap')


class LabelMap(mongoengine.EmbeddedDocument):
    """A label map with an optional associated color lookup table."""

    filename = fields.StringField(required=True)
    """The label map file path relative to the web app root."""
    
    color_table = fields.StringField()
    """The color map lookup table file path relative to the web app root."""


class ImageContainer(mongoengine.EmbeddedDocument):
    """
    The patient scan or registration.
    """

    meta = dict(allow_inheritance=True)

    name = fields.StringField(required=True)
    """The container name, e.g. scan ``t1`` or registration ``k3RtZ``."""

    files = fields.ListField(field=fields.StringField())
    """The image file pathnames relative to the web app root."""

    # TODO - is there a use case for several intensity measures
    # per container?
    intensity = fields.EmbeddedDocumentField('Intensity')


class Scan(ImageContainer):
    """The patient image scan."""
    
    registrations = fields.ListField(field=mongoengine.EmbeddedDocumentField('Registration'))
    """The registration {name: object} dictionary."""


class Registration(ImageContainer):
    """The patient image registration that results from processing
    the image scan."""

    parameters = fields.DictField()


class Intensity(mongoengine.EmbeddedDocument):
    """The image signal intensities for a given probe."""

    probe = fields.EmbeddedDocumentField('Probe')

    intensities = fields.ListField(field=fields.FloatField())
    """The list of series intensities."""


class Probe(mongoengine.EmbeddedDocument):
    """The image probe to conduct a measurement."""

    description = fields.StringField()
    """The short description, e.g. ``ROI centroid``"""

    location = fields.ListField(field=fields.FloatField())
    """The (x, y, z) probe coordinates"""


class SessionDetail(mongoengine.Document):
    """The MR session detailed content."""

    meta = dict(collection='qiprofile_session_detail')

    bolus_arrival_index = fields.IntField()

    series = fields.ListField(field=mongoengine.EmbeddedDocumentField('Series'))

    scans = fields.DictField(field=mongoengine.EmbeddedDocumentField('Scan'))
    """The scan {name: object} dictionary."""

    def clean(self):
        arv = self.bolus_arrival_index
        if arv:
            if not self.series:
                raise ValidationError("Session is missing any series")
            if arv < 0 or arv >= len(self.series):
                raise ValidationError("Bolus arrival index does not refer"
                                      " to a series")


class Treatment(mongoengine.EmbeddedDocument):
    """The patient therapy, e.g. adjuvant."""

    TYPE_CHOICES = ('Neoadjuvant', 'Primary', 'Adjuvant')

    treatment_type = fields.StringField(
        max_length=choices.max_length(TYPE_CHOICES),
        choices=TYPE_CHOICES)

    begin_date = fields.DateTimeField(required=True)

    end_date = fields.DateTimeField(required=True)
    
    drug_courses = fields.ListField(
        field=mongoengine.EmbeddedDocumentField('DrugCourse')
    )


class DrugCourse(mongoengine.EmbeddedDocument):
    
    drug_name = fields.StringField(required=True)
    
    administration = fields.ListField(
        field=mongoengine.EmbeddedDocumentField('DrugAdministration')
    )


class DrugAdministration(mongoengine.EmbeddedDocument):
    
    date = fields.DateTimeField()
    
    dosage = fields.EmbeddedDocumentField('Measurement')


class Measurement(mongoengine.EmbeddedDocument):
    
    value = fields.EmbeddedDocumentField('Value', required=True)
    
    unit = fields.EmbeddedDocumentField('Unit', required=True)
    
    # A unit factor, e.g. unit=WeightUnit(), per_unit = WeightUnit(scale='k'),
    # and value = 12 implies the dosage is 2mg/kg, where the kg is the
    # patient weight.
    per_unit = fields.EmbeddedDocumentField('Unit')


class Unit(mongoengine.EmbeddedDocument):

    meta = dict(allow_inheritance=True)


class ExtentUnit(Unit):

    SCALES = ['c', 'm']

    # The meter designator.
    base = fields.StringField(default='m')
    
    # The scale defaults to millimeter.
    scale = fields.StringField(choices=SCALES, default='m')


class WeightUnit(Unit):

    SCALES = ['c', 'm', 'k']

    # The gram designator.
    base = fields.StringField(default='g')
    
    # The scale defaults to milligram.
    scale = fields.StringField(choices=SCALES, default='m')


class VolumeUnit(Unit):

    SCALES = ['m']

    # The liter designator.
    base = fields.StringField(default='l')
    
    # The scale defaults to milliliter.
    scale = fields.StringField(choices=SCALES, default='m')


class Value(mongoengine.EmbeddedDocument):

    meta = dict(allow_inheritance=True)


class StringValue(Value):

    value = fields.StringField(required=True)


class NumericValue(Value):

    meta = dict(allow_inheritance=True)


class IntValue(NumericValue):
    
    value = fields.IntField(required=True)


class FloatValue(NumericValue):
    
    value = fields.FloatField(required=True)


class Encounter(mongoengine.EmbeddedDocument):
    """The patient clinical encounter, e.g. biopsy."""

    meta = dict(allow_inheritance=True)

    date = fields.DateTimeField(required=True)


class Assessment(Encounter):
    """Generic collection of outcomes."""

    evaluation = fields.EmbeddedDocumentField('GenericEvaluation')


class Biopsy(Encounter):
    """Non-therapeutic tissue extraction resulting in a pathology report."""

    pathology = fields.EmbeddedDocumentField('Pathology', required=True)


class Surgery(Encounter):
    """Therapeutic tissue extraction which usually results in a pathology report."""

    meta = dict(allow_inheritance=True)

    pathology = fields.EmbeddedDocumentField('Pathology')


class BreastSurgery(Surgery):
    """Breast tumor extraction."""

    TYPE_CHOICES = ('Mastectomy', 'Lumpectomy')

    surgery_type = fields.StringField(
        max_length=choices.max_length(TYPE_CHOICES),
        choices=TYPE_CHOICES)


class Evaluation(mongoengine.EmbeddedDocument):
    """The patient evaluation holds outcomes."""

    meta = dict(allow_inheritance=True)


class GenericEvaluation(Evaluation):
    """An unconstrained set of outcomes."""

    outcomes = fields.ListField(fields.EmbeddedDocumentField('Outcome'))


class Pathology(Evaluation):
    """The patient pathology summary."""

    meta = dict(allow_inheritance=True)

    tnm = fields.EmbeddedDocumentField('TNM')


class BreastPathology(Pathology):
    """The QIN breast patient pathology summary."""

    HER2_NEU_IHC_CHOICES = [(0, '0'), (1, '1+'), (2, '2+'), (3, '3+')]
    """The HER2 NEU IHC choices are displayed as 0, 1+, 2+, 3+."""

    class KI67Field(fields.IntField):
        def validate(self, value, clean=True):
            return value > 0 and value <= 100

    estrogen = fields.EmbeddedDocumentField('HormoneReceptorStatus')

    progestrogen = fields.EmbeddedDocumentField('HormoneReceptorStatus')

    her2_neu_ihc = fields.IntField(choices=HER2_NEU_IHC_CHOICES)

    her2_neu_fish = fields.BooleanField(choices=choices.POS_NEG_CHOICES)

    ki_67 = KI67Field()


class SarcomaPathology(Pathology):
    """The QIN sarcoma patient pathology summary."""

    HISTOLOGY_CHOICES = ('Carcinosarcoma', 'Cerebellar', 'Chondrosarcoma',
                         'Clear Cell', 'Dermatofibrosarcoma', 'Fibrosarcoma',
                         'Leiomyosarcoma', 'Liposarcoma', 'MFH', 'MPNST',
                         'Osteosarcoma', 'Rhabdomyosarcoma', 'Synovial', 'Other')

    site = fields.StringField()

    necrosis_pct = fields.EmbeddedDocumentField('NecrosisPercent')

    histology = fields.StringField(
        max_length=choices.max_length(HISTOLOGY_CHOICES),
        choices=HISTOLOGY_CHOICES)


## Clinical metrics ##

class Outcome(mongoengine.EmbeddedDocument):
    """The patient clinical outcome."""

    meta = dict(allow_inheritance=True)


class TNM(Outcome):
    """
    The TNM tumor staging. The TNM fields are as follows:
    
      * size - primary tumor size (T)

      * lymph_status - regional lymph nodes (N)

      * metastasis - distant metastasis (M)

      * grade - tumor grade (G)

      * serum_tumor_markers (S)

      * resection_boundaries (R)

      * lymphatic_vessel_invasion (L)

      * vein_invasion (V)
    
    The size is an aggregate Size field. 
    See http://www.cancer.gov/cancertopics/factsheet/detection/staging for
    an overview. See http://en.wikipedia.org/wiki/TNM_staging_system and
    http://cancerstaging.blogspot.com/ for the value definition.
        
    Note:: The size and lymph_status choices can be further constrained by
        tumor type. Since :class:`TNM` is a generic class, these constraints
        are not enforced in this TNM class. Rather, the REST client is
        responsible for enforcing additional choice constraints. The
        :meth:`TNM.lymph_status_choices` helper method can be used for
        tumor type specific choices. See :class:`TNM.Size`` for a discussion
        of the size constraints.
  """
    class Size(mongoengine.EmbeddedDocument):
        """
        The TNM primary tumor size field.
        
        Note:: The size score choices can be further constrained by tumor
            type. For example, the sarcoma tumor_size choices are 0, 1 or 2
            and suffix choices are ``a`` or ``b``. See :class:`TNM` for a
            discussion of choice constraints. The :meth:`TNM.Size.tumor_size_choices`
            and :meth:`TNM.Size.suffix_choices` helper methods can be used for
            tumor type specific choices.
        """

        PREFIXES = ['c', 'p', 'y', 'r', 'a', 'u']

        SUFFIXES = ['a', 'b', 'c']
        
        SUFFIX_CHOICES = dict(
            Any=['a', 'b', 'c'],
            Sarcoma=['a', 'b']
        )
        
        TUMOR_SIZE_CHOICES = dict(
            Any=range(0, 5),
            Sarcoma=range(0, 3)
        )

        SIZE_PAT = """
            ^(?P<prefix>c|p|y|r|a|u)?   # The prefix modifier
            T                           # The size designator
            (x |                        # Tumor cannot be evaluated
             (?P<in_situ>is) |          # Carcinoma in situ
             ((?P<tumor_size>0|1|2|3|4) # The size
              (?P<suffix>a|b|c)?        # The suffix modifier
             )
            )$
        """

        @staticmethod
        def tumor_size_choices(tumor_type=None):
            """
            @param tumor_type the optional tumor type, e.g. ``Breast``
            @return the tumor_size choices for the given type
            """
            if tumor_type not in TNM.Size.TUMOR_SIZE_CHOICES:
                tumor_type = 'Any'
            
            return TNM.Size.TUMOR_SIZE_CHOICES[tumor_type]

        @staticmethod
        def suffix_choices(tumor_type=None):
            """
            @param tumor_type the optional tumor type, e.g. ``Breast``
            @return the suffix choices for the given type
            """
            if tumor_type not in TNM.Size.SUFFIX_CHOICES:
                tumor_type = 'Any'
            
            return TNM.Size.SUFFIX_CHOICES[tumor_type]

        SIZE_REGEX = re.compile(SIZE_PAT, re.VERBOSE)
        """The TNM size validation regular expression."""

        prefix = fields.StringField(choices=PREFIXES)

        tumor_size = fields.IntField(choices=TUMOR_SIZE_CHOICES['Any'])

        class InSitu(mongoengine.EmbeddedDocument):
            INVASIVE_TYPE_CHOICES = ('ductal', 'lobular')
            
            invasive_type = fields.StringField(choices=INVASIVE_TYPE_CHOICES)

        in_situ = fields.EmbeddedDocumentField(InSitu)

        suffix = fields.StringField(choices=SUFFIX_CHOICES['Any'])

        def __str__(self):
            prefix = self.prefix or ''
            suffix = self.suffix or ''
            if self.in_situ:
                size = 'is'
            elif self.tumor_size:
                size = str(self.tumor_size)
            else:
                size = 'x'
            
            return "%sT%s%s" % (prefix, size, suffix)
        
        @classmethod
        def parse(klass, value):
          """
          Parses the given string into a new Size.
          
          @param value the input string
          @return the new Size object
          """
          match = klass.SIZE_REGEX.match(value)
          return klass(**match.groupdict())

        def clean(self):
            """
            Peforms document-level validation.

            @raise ValidationError if the in_situ flag is set but there is a
              tumor_size or suffix field
            """
            if self.in_situ:
                if self.tumor_size != None:
                    raise ValidationError("TNM Size with in_situ flag set to"
                                          " True cannot have tumor_size %d" %
                                          self.tumor_size)
                if self.suffix != None:
                    raise ValidationError("TNM Size with in_situ flag set to"
                                          " True cannot have a suffix %s" %
                                          self.suffix)
            return True
        
    LYMPH_STATUS_CHOICES = dict(
        Any=range(0, 4),
        Sarcoma=range(0, 2)
    )

    tumor_type = fields.StringField(required=True)

    size = fields.EmbeddedDocumentField(Size)

    # TODO - make lymph status an aggregate with suffix modifiers,
    # including 'mi'.
    lymph_status = fields.IntField(choices=LYMPH_STATUS_CHOICES['Any'])

    metastasis = fields.BooleanField(choices=choices.POS_NEG_CHOICES)

    grade = fields.EmbeddedDocumentField('Grade')

    serum_tumor_markers = fields.IntField(choices=range(0, 4))

    resection_boundaries = fields.IntField(choices=range(0, 3))

    lymphatic_vessel_invasion = fields.BooleanField()

    vein_invasion = fields.IntField(choices=range(0, 3))

    @staticmethod
    def lymph_status_choices(tumor_type=None):
        """
        @param tumor_type the optional tumor type, e.g. ``Breast``
        @return the lymph_status choices for the given type
        """
        if tumor_type not in TNM.LYMPH_STATUS_CHOICES:
            tumor_type = 'Any'
        
        return TNM.LYMPH_STATUS_CHOICES[tumor_type]


class Grade(Outcome):
    """
    The abstract tumor grade superclass, specialized for each
    tumor type.
    """

    meta = dict(allow_inheritance=True)

    composite = fields.IntField(choices=range(1, 4))


class NottinghamGrade(Grade):
    """The Nottingham breast tumor grade."""

    COMPONENT_CHOICES = range(1, 4)

    tubular_formation = fields.IntField(choices=COMPONENT_CHOICES)
    
    nuclear_pleomorphism = fields.IntField(choices=COMPONENT_CHOICES)
    
    mitotic_count = fields.IntField(choices=COMPONENT_CHOICES)


class HormoneReceptorStatus(Outcome):
    """The patient estrogen/progesterone hormone receptor status."""

    class IntensityField(fields.IntField):
        def validate(self, value, clean=True):
            return value > 0 and value <= 100

    hormone = fields.StringField(required=True)

    positive = fields.BooleanField(choices=choices.POS_NEG_CHOICES)

    quick_score = fields.IntField(choices=range(0, 9))

    intensity = IntensityField()


class FNCLCCGrade(Grade):
    """The FNCLCC sarcoma tumor grade."""

    differentiation = fields.IntField(choices=range(1, 4))

    mitotic_count = fields.IntField(choices=range(1, 4))

    necrosis = fields.IntField(choices=range(0, 3))


class NecrosisPercent(Outcome):
    """The necrosis percent value or range."""
    pass


class NecrosisPercentValue(NecrosisPercent):
    """The necrosis percent absolute value."""

    value = fields.IntField(choices=range(0, 101))


class NecrosisPercentRange(NecrosisPercent):
    """The necrosis percent range."""

    class Bound(mongoengine.EmbeddedDocument):
        """
        Necrosis percent upper or lower bound abstract class.
        The subclass is responsible for adding the ``inclusive``
        field.
        """

        meta = dict(allow_inheritance=True)

        value = fields.IntField(choices=range(0, 101))


    class LowerBound(Bound):
        """Necrosis percent lower bound."""

        inclusive = fields.BooleanField(default=True)


    class UpperBound(Bound):
        """Necrosis percent upper bound."""

        inclusive = fields.BooleanField(default=False)

    start = fields.EmbeddedDocumentField(LowerBound)

    stop = fields.EmbeddedDocumentField(UpperBound)

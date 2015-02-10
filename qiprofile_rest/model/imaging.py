"""
The qiprofile imaging Mongodb data model.
"""

import re
import decimal
from numbers import Number
import mongoengine
from mongoengine import (fields, signals, ValidationError)
from .. import choices

class Session(mongoengine.EmbeddedDocument):
    """The MR session (a.k.a. *study* in DICOM terminology)."""

    number = fields.IntField(required=True)

    acquisition_date = fields.DateTimeField()

    detail = fields.ReferenceField('SessionDetail')

    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        """Cascade delete this Session's detail."""

        if self.detail:
            self.detail.delete()

signals.pre_delete.connect(Session.pre_delete, sender=Session)


class VoxelSize(mongoengine.EmbeddedDocument):
    """The voxel width, depth and spacing."""
    
    width = fields.FloatField()
    """
    The voxel width (= voxel length) in millimeters. For an MR,
    the width is the DICOM Pixel Spacing value.
    """
    
    depth = fields.FloatField()
    """
    The voxel depth in millimeters. For an MR, the depth is the
    DICOM Slice Thickness.
    """
    
    spacing = fields.FloatField()
    """The inter-slice spacing in millimeters. For an MR, the spacing
    is the DICOM Spacing Between Slices.
    """


class Point(mongoengine.EmbeddedDocument):
    """3D point in volume voxel space."""
    
    x = fields.IntField()
    """
    The horizontal dimension coordinate in the plane perpendicular
    to the slice depth dimension.
    """
    
    y = fields.IntField()
    """
    The vertical dimension coordinate in the plane perpendicular
    to the slice depth dimension.
    """
    
    z = fields.IntField()
    """
    The slice depth dimension.
    """


class LineSegment(mongoengine.EmbeddedDocument):
    """The (begin, end) points of a line segment in volume voxel space."""
    
    begin = fields.EmbeddedDocumentField('Point')
    
    end = fields.EmbeddedDocumentField('Point')


class Region(mongoengine.EmbeddedDocument):
    """The 3D region in volume voxel space."""

    mask = fields.StringField()
    """The binary mask file name."""
    
    length_segment = fields.EmbeddedDocumentField(LineSegment)
    """The region segment with maximal x difference."""
    
    width_segment = fields.EmbeddedDocumentField(LineSegment)
    """The region segment with maximal y difference."""
    
    depth_segment = fields.EmbeddedDocumentField(LineSegment)
    """The region segment with maximal z difference."""
        
    centroid = mongoengine.EmbeddedDocumentField(Point)
    """The region centroid."""

    centroid_intensity = fields.FloatField()
    """The signal intensity at the centroid."""


class Volume(mongoengine.EmbeddedDocument):

    filename = fields.ListField(field=fields.StringField())
    """The image file pathname relative to the web app root."""

    average_intensity = field=fields.FloatField()
    """The image signal intensity over the entire volume."""


class LabelMap(mongoengine.EmbeddedDocument):
    """A label map with an optional associated color lookup table."""

    filename = fields.StringField(required=True)
    """The label map file path relative to the web app root."""

    color_table = fields.StringField()
    """The color map lookup table file path relative to the web app root."""


class Modeling(mongoengine.EmbeddedDocument):
    """
    The QIN pharmicokinetic modeling run over a consistent list of image
    containers.
    """

    technique = fields.StringField()

    input_parameters = fields.DictField()
    """The modeling execution input parameters."""

    results = fields.ListField(
        fields.EmbeddedDocumentField('ModelingResult')
    )
    """
    The modeling results in session number order.
    """


class ModelingResult(mongoengine.EmbeddedDocument):
    """The QIN pharmicokinetic modeling result."""

    resource = fields.StringField(required=True)
    """The modeling XNAT resource name, e.g. ``pk_R3y9``."""

    fxl_k_trans = fields.EmbeddedDocumentField('ModelingParameter')

    fxr_k_trans = fields.EmbeddedDocumentField('ModelingParameter')

    delta_k_trans = fields.EmbeddedDocumentField('ModelingParameter')

    v_e = fields.EmbeddedDocumentField('ModelingParameter')

    tau_i = fields.EmbeddedDocumentField('ModelingParameter')

    def __str__(self):
        return "Modeling %s" % self.name


class ModelingParameter(mongoengine.EmbeddedDocument):
    """The discrete modeling result."""

    filename = fields.StringField(required=True)
    """The voxel-wise mapping file path relative to the web app root."""

    average = fields.FloatField(required=True)
    """The average parameter value over all voxels."""

    label_map = fields.EmbeddedDocumentField('LabelMap')


class ImageSequence(mongoengine.EmbeddedDocument):
    """
    The scan or registration image volume container.
    """

    meta = dict(allow_inheritance=True)
    
    volumes = fields.ListField(field=mongoengine.EmbeddedDocumentField(Volume))
    """
    The images in the sequence.
    """
    
    roi = fields.EmbeddedDocumentField('Region')
    
    voxel_size = fields.EmbeddedDocumentField(VoxelSize)
    """The voxel size in millimeters."""

    modeling = fields.DictField(field=fields.EmbeddedDocumentField('Modeling'))
    """
    PK modeling performed on the image sequence.
    """


class Registration(ImageSequence):
    """
    The patient image registration that results from processing a scan.
    """
    
    class Protocol(mongoengine.EmbeddedDocument):
        """
        The registration settings.
        """
    
        TECHNIQUE = ['ANTS', 'FNIRT']

        technique = fields.StringField(
            choices=TECHNIQUE,
            max_length=choices.max_length(TECHNIQUE),
            required=True
        )
        """The registration technique."""

        parameters = fields.DictField()
        """The registration input parameters."""

    resource = fields.StringField(required=True)
    """The registration XNAT resource name, e.g. ``reg_k3RtZ``."""


class Scan(ImageSequence):
    class Protocol(mongoengine.EmbeddedDocument):
        """
        A consistent set of scans for a given scan type. This is the concrete
        subclass of the abstract :class:`ImageSequence` class for scans.
        """

        scan_type = fields.StringField(required=True)
        """
        The scan type designation, e.g. ``T1``. This is represented in
        XNAT by the Scan *type* attribute.

        :Note: The :class:`qiprofile_rest.model.subject.Subject` holds a
          {scan type: scan set} dictionary, where the key is the lower-case,
          underscore representation of the corresponding scan type.
        """
    
        description = fields.StringField()
        """
        The image acquisition scan description, e.g. 'T1 SPIN ECHO'.
        This field is customarily specified as the DICOM Series Description
        or Protocol Name tag.
        """

    registration = fields.ListField(
        field=fields.EmbeddedDocumentField(Registration.Protocol)
    )
    """
    The registrations performed on the scan.
    """


class SessionDetail(mongoengine.Document):
    """The MR session detailed content."""

    meta = dict(collection='qiprofile_session_detail')

    bolus_arrival_index = fields.IntField()

    scans = fields.DictField(field=mongoengine.EmbeddedDocumentField(Scan))
    """
    The {scan type: Scan} dictionary, where the key is the lower-case,
    underscore representation of the
    :meth:`qiprofile_rest.model.ScanSet.scan_type` value.
    """

    def clean(self):
        arv = self.bolus_arrival_index
        if arv:
            if not self.volumes:
                raise ValidationError("Session does not have a volume")
            if arv < 0 or arv >= len(self.volumes):
                raise ValidationError(("Bolus arrival index does not refer"
                                       " to a valid volume index: %d") % arv)

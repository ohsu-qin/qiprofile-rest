from rest_framework import serializers
from .models import (Subject, SubjectDetail)


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject

    def save_object(self, obj, **kwargs):
        """
        If this is a create indicated by the ``force_insert`` keyword flag,
        then this method overrides
        '`rest_framework.serializers.BaseSerializer.save_object``
        to reference a new :class:`qiprofile.models.SubjectDetail`.
        """
        if 'force_insert' in kwargs and not obj.detail:
            obj.detail = SubjectDetail.objects.create()
        super(SubjectSerializer, self).save_object(obj, **kwargs)


class SubjectDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectDetail

from rest_framework import serializers
from .models import (User, Subject, SubjectDetail, SessionDetail)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User


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


class SessionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionDetail

    def to_native(self, obj):
        """
        Work around the following Django/REST/Mongo Engine bug:

        * The SessionDetail scan embedded field ``field_to_native`` method
          returns the string ``Scan object`` instead of the JSON object.
          There is no other known occurrence of this bug, and the cause
          defies isolation.
        """
        val_dict = super(SessionDetailSerializer, self).to_native(obj)
        scan_val = val_dict['scan']
        if isinstance(scan_val, str) or isinstance(scan_val, unicode):
            val_dict['scan'] = {field.attname: field.value_from_object(obj.scan)
                                for field in obj.scan._meta.fields}
            
        return val_dict

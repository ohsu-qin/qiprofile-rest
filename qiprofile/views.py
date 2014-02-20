import os
from django.views.decorators.csrf import csrf_exempt
from rest_framework import (generics, mixins, viewsets)
import bson
from .models import (Subject, SubjectDetail)
from .serializers import (SubjectSerializer, SubjectDetailSerializer)


class InvalidFilter(Exception):
    pass


class SubjectViewSet(viewsets.ModelViewSet):
    model = Subject
    serializer_class = SubjectSerializer
    filter_fields = ('project', 'collection')       
    
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        # The pk argument is either a Mongodb ID or a subject number.
        # If the pk is a subject number, then the request must include
        # a project and collection.
        if 'pk' in kwargs:
            try:
                bson.objectid.ObjectId(kwargs['pk'])
                self.lookup_field = 'pk'
            except bson.objectid.InvalidId:
                sbj_nbr = kwargs['number'] = kwargs.pop('pk')
                self.lookup_field = 'number'
                for field in ['project', 'collection']
                if field not in request.GET:
                    raise InvalidFilter("The subject %s request does not"
                                        " include a %s" % (sbj_nbr, field))

        return super(SubjectViewSet, self).dispatch(request, *args, **kwargs)
        

class SubjectDetailViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    model = SubjectDetail
    serializer_class = SubjectDetailSerializer

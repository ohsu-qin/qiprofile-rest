from rest_framework import routers
from .views import (SubjectViewSet, SubjectDetailViewSet)

router = routers.SimpleRouter()
router.register(r'subjects', SubjectViewSet)
router.register(r'subject-detail', SubjectDetailViewSet)

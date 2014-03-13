from rest_framework import routers
from .views import (UserViewSet, SubjectViewSet, SubjectDetailViewSet)

router = routers.SimpleRouter()
router.register(r'user', UserViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'subject-detail', SubjectDetailViewSet)

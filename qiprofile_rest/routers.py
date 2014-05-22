from rest_framework import routers
from .views import (UserViewSet, SubjectViewSet,
                    SubjectDetailViewSet, SessionDetailViewSet)

router = routers.SimpleRouter()
router.register(r'user', UserViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'subject[_-]detail', SubjectDetailViewSet)
router.register(r'session[_-]detail', SessionDetailViewSet)

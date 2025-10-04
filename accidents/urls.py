from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CrashViewSet

router = DefaultRouter()
router.register(r'crashes', CrashViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'boards', views.BoardViewSet)
router.register(
    r'boards/(?P<board_ln>[^/.]+)/threads', views.ThreadViewSet)
router.register(
    r'boards/(?P<board_ln>[^/.]+)/posts', views.PostViewSet)

urlpatterns = router.urls

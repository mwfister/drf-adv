from django.urls import include, path

from recipe import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('tags', views.TagViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]

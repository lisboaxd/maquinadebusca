from django.contrib import admin
from django.urls import path

from rest_framework.routers import DefaultRouter
from coletor.views import ColetorListView

router = DefaultRouter()
router.register('iniciar', ColetorListView)
urlpatterns = router.urls

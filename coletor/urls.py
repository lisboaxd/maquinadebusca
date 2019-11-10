from django.contrib import admin
from django.urls import path

from rest_framework.routers import DefaultRouter
from coletor.views import ColetorListView, ColetorView, LinksView

router = DefaultRouter()
router.register('iniciar', ColetorListView)
urlpatterns = router.urls
urlpatterns += [
    path('coletor/iniciar/', ColetorView.as_view(), name='iniciar'),
    path('coletor/links/', LinksView.as_view(), name='links')
]

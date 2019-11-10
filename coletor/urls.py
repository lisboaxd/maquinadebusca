from django.contrib import admin
from django.urls import path

from rest_framework.routers import DefaultRouter
from coletor.views import ColetorView, DocumentoViewSet, HostViewSet, LinkViewSet

router = DefaultRouter()
#router.register('iniciar', ColetorListView)
router.register('documento', DocumentoViewSet)
router.register('host', HostViewSet)
router.register('link', LinkViewSet)
urlpatterns = router.urls
urlpatterns += [
    path('iniciar/', ColetorView.as_view(), name='iniciar'),
    path('documento/', ColetorView.as_view(), name='links'),
    path('documento/<int:id>', ColetorView.as_view(), name='links'),
    path('links/', ColetorView.as_view(), name='links'),
    path('links/<int:id>', ColetorView.as_view(), name='links'),
    path('host/', ColetorView.as_view(), name='links'),
    path('host/<int:id>', ColetorView.as_view(), name='links'),
    
]

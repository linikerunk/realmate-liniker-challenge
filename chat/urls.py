from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'chat'

router = DefaultRouter()
router.register(r'contacts', views.ContactViewSet, basename='contact')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'auto-responses', views.AutoResponseViewSet, basename='autoresponse')

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('', include(router.urls)),
]

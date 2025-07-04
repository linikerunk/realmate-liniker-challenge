"""
URL configuration for realmate_challenge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

app_name = 'chat'

routes = DefaultRouter()

urlpatterns = [
    path('webhook/', views.WebhookView.as_view(), name='webhook'),
    path('conversations/', views.ListConversationsView.as_view(), name='conversation-list'),
    path('conversations/<uuid:id>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
]

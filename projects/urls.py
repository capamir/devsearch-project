from django.urls import path
from . import views

urlpatterns = [
    path('', views.projects, name='projects'),
    path('create-project', views.createProject, name='create-project'),
    path('<str:pk>', views.project, name='single-project'),
]

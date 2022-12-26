from django.urls import path
from . import views

urlpatterns = [
    path('', views.projects, name='projects'),
    path('create-project/', views.createProject, name='create-project'),
    path('<str:pk>/', views.project, name='single-project'),
    path('update-project/<str:pk>/', views.updateProject, name='update-project'),
    path('delete-project/<str:pk>/', views.deleteProject, name='delete-project'),

]

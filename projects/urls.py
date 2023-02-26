from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectsView.as_view(), name='projects'),
    path('create-project/', views.ProjectCreateView.as_view(), name='create-project'),
    path('<str:pk>/', views.ProjectView.as_view(), name='single-project'),
    path('update-project/<str:pk>/', views.ProjectUpdateView.as_view(), name='update-project'),
    path('delete-project/<str:pk>/', views.ProjectDeleteView.as_view(), name='delete-project'),

]

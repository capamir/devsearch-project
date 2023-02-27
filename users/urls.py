from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),

    path('account/', views.UserAccountView.as_view(), name='account'),
    path('edit-account/', views.UserEditAccountView.as_view(), name='edit-account'),
    path('inbox/', views.InboxView.as_view(), name='inbox'),

    path('create-skill/', views.SkillCreateView.as_view(), name='create-skill'),

    path('', views.ProfilesView.as_view(), name='profiles'),
    path('profile/<str:pk>/', views.ProfileDetailView.as_view(), name='single-profile'),

    path('update-skill/<str:pk>/', views.SkillUpdateView.as_view(), name='update-skill'),
    path('delete-skill/<str:pk>/', views.SkillDeleteView.as_view(), name='delete-skill'),

    path('message/<str:pk>/', views.MessageView.as_view(), name='message'),
    path('send-message/<str:pk>/', views.MessageCreateView.as_view(), name='send-message'),

]

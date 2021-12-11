from django.urls import path

from . import views


urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.TokenObtainPairView.as_view(), name='login'),
    path('user_info/', views.UserInfoView.as_view(), name='user_info'),
    path('refresh/', views.TokenRefreshView.as_view(), name='refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]


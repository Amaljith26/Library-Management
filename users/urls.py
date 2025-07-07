from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import (
    HomeView, DashboardView, SignupView,
    custom_login_view, admin_dashboard,
    faculty_dashboard, member_dashboard,verify_member
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    path('login/', custom_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('delete-member/<int:id>/', views.delete_member, name='delete-member'),

    path('admin-dashboard/', admin_dashboard, name='admin-dashboard'),
    path('faculty-dashboard/', faculty_dashboard, name='faculty-dashboard'),
    path('member-dashboard/', member_dashboard, name='member-dashboard'),
    path('verify-member/<int:member_id>/', views.verify_member, name='verify_member'),
    
]

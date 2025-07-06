from django.urls import path
from . import views
from .views import update_member,MemberPaginatedListView,edit_member

urlpatterns = [
    path('dashboard/', views.member_dashboard, name='member_dashboard'),
    path('update/', views.update_member, name='update_member'),
    path('profile/', views.profile_view, name='user_profile'),
    path('member-list/', MemberPaginatedListView.as_view(), name='member_list'),
    path('edit-member/<int:member_id>/', edit_member, name='edit_member'),

]
from django.urls import path
from . import views

urlpatterns = [
    path('request/<int:book_id>/', views.request_borrow, name='request_borrow'),
    path('approve/<int:request_id>/', views.approve_borrow, name='approve_borrow'),
    path('return/<int:request_id>/', views.mark_returned, name='mark_returned'),
    path('my-requests/', views.my_borrow_requests, name='my_borrow_requests'),
]

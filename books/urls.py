from django.urls import path
from .import views
from .views import BookListView, AddBookView, UpdateBookView,BookPaginatedListView

urlpatterns = [
    path('Book List', BookListView.as_view(), name='book-list'),
    path('books/add/', AddBookView.as_view(), name='add_book'),
    path('books/update/<int:pk>/', UpdateBookView.as_view(), name='update_book'),
    path('books/paginated/', BookPaginatedListView.as_view(), name='book_paginated_list'),
    path('favorites/', views.favorite_books, name='favorite_books'),
    path('favorites/add/<int:book_id>/', views.add_to_favorites, name='add_to_favorites'),  
    path('favorites/remove/<int:book_id>/', views.remove_from_favorites, name='remove_from_favorites'), 
]

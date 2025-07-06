from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre','author', 'status', 'stock')
    search_fields = ('title', 'isbn', 'author')
    list_filter = ('status', 'genre', 'language')


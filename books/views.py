from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Book,FavoriteBook
from .forms import BookForm
from django.contrib import messages

from django.views.generic import TemplateView
from django.shortcuts import render,get_object_or_404,redirect
from collections import defaultdict

from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import BookSerializer

class BookListView(TemplateView):
    template_name = 'books/book_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = Book.objects.all().order_by('genre')

        genre_books = defaultdict(list)
        for book in books:
            genre_books[book.genre].append(book)

        context['genre_books'] = dict(genre_books)
        return context



class AddBookView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/add_book.html'
    success_url = reverse_lazy('book_paginated_list')

    

class UpdateBookView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/update_book.html'
    success_url = reverse_lazy('book_paginated_list')
    
    def form_valid(self, form):
        self.request.session['update_success'] = "Book details updated successfully."
        return super().form_valid(form)


class BookPaginatedListView(TemplateView):
    template_name = 'books/book_paginated_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')

        if query:
            books = Book.objects.filter(title__icontains=query) | Book.objects.filter(author__icontains=query)
        else:
            books = Book.objects.all()

        books = books.order_by('-id')
        paginator = Paginator(books, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if 'update_success' in self.request.session:
            context['update_success'] = self.request.session.pop('update_success')

        context['page_obj'] = page_obj
        context['request'] = self.request  
        return context
    
@login_required
def add_to_favorites(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    FavoriteBook.objects.get_or_create(user=request.user, book=book)
    return redirect('book-list') 


@login_required
def favorite_books(request):
    favorites = FavoriteBook.objects.filter(user=request.user).select_related('book')
    return render(request, 'books/favourite_books.html', {'favorites': favorites})

@login_required
def remove_from_favorites(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    FavoriteBook.objects.filter(user=request.user, book=book).delete()
    return redirect('favorite_books')


@api_view(['GET'])
def book_list(request):
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)
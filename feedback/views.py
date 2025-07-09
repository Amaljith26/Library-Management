from django.shortcuts import get_object_or_404, redirect, render
from books.models import Book
from .models import Review
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required


@login_required
def add_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    try:
        review = Review.objects.get(user=request.user, book=book)
    except Review.DoesNotExist:
        review = None

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.user = request.user
            new_review.book = book
            new_review.save()
            return redirect('book-list') 
    else:
        form = ReviewForm(instance=review)

    return render(request, 'feedback/add_review.html', {
        'form': form,
        'book': book,
    })

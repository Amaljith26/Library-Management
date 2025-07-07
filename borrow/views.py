from django.shortcuts import render, redirect, get_object_or_404
from .models import BorrowRequest
from books.models import Book
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Max
from django.contrib import messages
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import BorrowRequestSerializer


@login_required
def request_borrow(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    existing = BorrowRequest.objects.filter(user=request.user, book=book, status__in=['pending', 'approved']).exists()
    if existing:
        messages.warning(request, "You already have a pending or approved request for this book.")
    elif book.status == 'available' and book.stock > 0:
        BorrowRequest.objects.create(user=request.user, book=book)
        messages.success(request, "Borrow request submitted.")
    else:
        messages.error(request, "Book is currently not available for borrowing.")

    return redirect('my_borrow_requests')

@login_required
def my_borrow_requests(request):
    borrow = BorrowRequest.objects.all()
    latest_requests = (
        BorrowRequest.objects
        .filter(user=request.user)
        .values('book')
        .annotate(latest_id=Max('id'))
        .values_list('latest_id', flat=True)
    )
    borrow_requests = BorrowRequest.objects.filter(id__in=latest_requests).order_by('-request_date')
    return render(request, 'borrow/my_borrow_requests.html', {
        'borrow_requests': borrow_requests,
        'borrow':borrow
    })

@login_required
def approve_borrow(request, request_id):
    borrow = get_object_or_404(BorrowRequest, id=request_id, status='pending')
    borrow.status = 'approved'
    borrow.issue_date = timezone.now()
    borrow.due_date = timezone.now() + timedelta(days=14)
    borrow.book.stock -= 1
    borrow.book.save()
    borrow.save()
    return redirect('faculty-dashboard')

@login_required
def mark_returned(request, request_id):
    borrow = get_object_or_404(BorrowRequest, id=request_id, status='approved')
    borrow.status = 'returned'
    borrow.return_date = timezone.now()
    borrow.calculate_fine()
    borrow.book.stock += 1
    borrow.book.save()
    borrow.save()
    return redirect('faculty-dashboard')



@api_view(['GET', 'POST'])
def borrow_request_list(request):
    if request.method == 'GET':
        borrow_requests = BorrowRequest.objects.all()
        serializer = BorrowRequestSerializer(borrow_requests, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = BorrowRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

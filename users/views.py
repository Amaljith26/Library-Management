from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from books.models import Book

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm  
from django.contrib.auth.forms import AuthenticationForm
from memberships.models import Member
from borrow.models import BorrowRequest
from django.db.models import Max
from django.utils import timezone
from datetime import timedelta


class HomeView(View):
    def get(self, request):
        return render(request, 'base.html')
    

def custom_login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            role = request.POST.get('role')

            user = authenticate(request, username=username, password=password)

            if user:
                if hasattr(user, 'role') and user.role == role:
                    login(request, user)
                    request.session['role'] = role

                    if role == 'admin':
                        return redirect('admin-dashboard')
                    elif role == 'faculty':
                        return redirect('faculty-dashboard')
                    else:
                        return redirect('member-dashboard')
                else:
                    messages.error(request, f"You are not authorized to log in as {role.title()}.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        role = request.user.role
        if role == 'admin':
            return render(request, 'users/admin_dashboard.html')
        elif role == 'librarian':
            return render(request, 'users/librarian_dashboard.html')
        elif role == 'member':
            return render(request, 'users/member_dashboard.html')
        return redirect('home')
    


class SignupView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('login')


@login_required
def admin_dashboard(request):
    total_books = Book.objects.count()
    members_count = User.objects.filter(role='member').count()
    faculty_count = User.objects.filter(role='faculty').count()

    members = User.objects.filter(role='member').order_by('-id')[:5]
    faculty_members = User.objects.filter(role='faculty').order_by('-id')[:5]

    member_form = CustomUserCreationForm(prefix="member")
    faculty_form = CustomUserCreationForm(prefix="faculty")

    if request.method == "POST":
        if 'add_member' in request.POST:                      #here the add_member is the name given inside the class
            member_form = CustomUserCreationForm(request.POST, prefix="member")
            if member_form.is_valid():
                user = member_form.save(commit=False)
                user.role = 'member'
                user.save()
                messages.success(request, "Member added successfully!")
                return redirect('admin-dashboard')

        elif 'add_faculty' in request.POST:
            faculty_form = CustomUserCreationForm(request.POST, prefix="faculty")
            if faculty_form.is_valid():
                user = faculty_form.save(commit=False)
                user.role = 'faculty'
                user.save()
                messages.success(request, "Faculty added successfully!")
                return redirect('admin-dashboard')

    return render(request, 'users/admin_dashboard.html', {
        'form': member_form,
        'faculty_form': faculty_form,
        'total_books': total_books,
        'members_count': members_count,
        'faculty_count': faculty_count,
        'members': members,
        'faculty_members': faculty_members,
    })


@login_required
def member_dashboard(request):
    
    if request.user.role not in ['member', 'admin']:
        messages.error(request, "You are not authorized to access the member dashboard.")
        return redirect('dashboard')
    return render(request, 'users/member_dashboard.html')


def is_faculty(user):
    return user.is_authenticated and user.role == 'faculty'

@login_required
def faculty_dashboard(request):
    books = Book.objects.all().order_by('-id')[:5]
    if request.user.role not in ['faculty', 'admin']:
        messages.error(request, "Access denied. Only faculty or admin can view this page.")
        return redirect('login')  

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'member'  
            user.save()
            messages.success(request, "Member added successfully!")
            return redirect('faculty-dashboard')
    else:
        form = CustomUserCreationForm()

    members = User.objects.filter(role='member').order_by('-id')[:5]
    total_books = Book.objects.count()
    total_books_available = Book.objects.filter(status='available').count()
    latest_requests = (
    BorrowRequest.objects
    .values('user', 'book')
    .annotate(latest_id=Max('id'))
    .values_list('latest_id', flat=True)
    )

    borrow_requests = BorrowRequest.objects.select_related('user', 'book').filter(id__in=latest_requests).order_by('-request_date')
    members_profile = Member.objects.filter(is_verified_by_faculty=False)
    return render(request, 'users/faculty_dashboard.html', {
        'form': form,
        'members': members,
        'books':books,
        'total_books':total_books,
        'total_books_available':total_books_available,
        'members_profile': members_profile,  
        'borrow_requests':borrow_requests,
    })


@login_required
@user_passes_test(is_faculty)
def verify_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    member.is_verified_by_faculty = True
    member.save()
    return redirect('faculty-dashboard')


def is_faculty(user):
    return user.is_authenticated and user.role == 'faculty'

@login_required
@user_passes_test(is_faculty)
def delete_member(request, id):
    member = get_object_or_404(User, id=id, role='member')
    member.delete()
    messages.success(request, "Member deleted successfully.")
    return redirect('faculty-dashboard')


@login_required
def approve_borrow(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)

    if borrow_request.status == 'pending' and borrow_request.book.status == 'available' and borrow_request.book.stock > 0:
        borrow_request.status = 'approved'
        borrow_request.approved_date = timezone.now()
        borrow_request.due_date = timezone.now() + timedelta(days=14)
        borrow_request.save()

        # Reduce stock
        book = borrow_request.book
        book.stock -= 1
        if book.stock == 0:
            book.status = 'unavailable'
        book.save()
        
        messages.success(request, f"Borrow request for '{book.title}' has been approved.")
    else:
        messages.error(request, "Request cannot be approved.")
    
    return redirect('faculty-dashboard')


@login_required
def mark_returned(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    borrow = BorrowRequest.objects.all()
    
    if borrow_request.status == 'approved':
        borrow_request.status = 'returned'
        borrow_request.returned_date = timezone.now()
        
        
        if borrow_request.due_date and borrow_request.returned_date > borrow_request.due_date:
            days_late = (borrow_request.returned_date - borrow_request.due_date).days
            borrow_request.fine = days_late * 10  # Example: ₹5 per day fine
        borrow_request.save()

        
        book = borrow_request.book
        book.stock += 1
        book.status = 'available'
        book.save()

        messages.success(request, f"Marked '{book.title}' as returned.")
    else:
        messages.error(request, "Cannot mark this request as returned.")

    return redirect('faculty-dashboard')

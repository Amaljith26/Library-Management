from django.shortcuts import render, redirect
from .forms import MemberUpdateForm
from .models import Member
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from memberships.models import Member


def member_dashboard(request):
    user = request.user
    try:
        member = user.member_profile
    except Member.DoesNotExist:
        return redirect('update_member')  
    if not member.membership_type or not member.plan_type:
        return redirect('update_member')

    context = {
        'member': member,
        'can_borrow': member.is_active()
    }
    return render(request, 'users/member_dashboard.html', context)


@login_required
def update_member(request):
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        member = None

    if request.method == 'POST':
        if member is None:
            member = Member(user=request.user, start_date=timezone.now().date()) 

        form = MemberUpdateForm(request.POST,request.FILES, instance=member)
        if form.is_valid():
            member = form.save(commit=False)
         
            if member.plan_type == 'Annual':
                member.expiry_date = member.start_date + timezone.timedelta(days=365)
            elif member.plan_type == 'Semi-Annual':
                member.expiry_date = member.start_date + timezone.timedelta(days=182)
            member.save()
            return redirect('member_dashboard')
    else:
        form = MemberUpdateForm(instance=member)
    return render(request, 'users/update_member.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, 'users/profile.html')


User = get_user_model()
def is_faculty_or_admin(user):
    return user.is_authenticated and (user.role == "faculty" or user.is_staff)



@method_decorator([login_required, user_passes_test(is_faculty_or_admin)], name='dispatch')
class MemberPaginatedListView(TemplateView):
    template_name = 'memberships/member_paginated_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')

        if query:
            members = User.objects.filter(role="member").filter(
                username__icontains=query
            ) | User.objects.filter(role="member").filter(
                email__icontains=query
            )
        else:
            members = User.objects.filter(role="member")

        members = members.order_by('-id')
        paginator = Paginator(members, 10)  
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['query'] = query
        return context


from django.shortcuts import render, get_object_or_404, redirect
from .forms import UserMemberUpdateForm


User = get_user_model()
@login_required
def edit_member(request, member_id):
    user = get_object_or_404(Member, id=member_id)
    if request.method == 'POST':
        form = UserMemberUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = UserMemberUpdateForm(instance=user)

    return render(request, 'memberships/edit_member.html', {'form': form, 'member': user})


def member_list_view(request):
    query = request.GET.get('q', '')
    members = Member.objects.all()
    if query:
        members = members.filter(name__icontains=query) | members.filter(email__icontains=query)

    return render(request, 'memberships/members_list.html', {'members': members})

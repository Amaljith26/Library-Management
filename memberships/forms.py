from django import forms
from .models import Member

class MemberUpdateForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [ 'phone', 'address', 'profile']

class UserMemberUpdateForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['plan_type', 'membership_type', 'is_verified_by_faculty']
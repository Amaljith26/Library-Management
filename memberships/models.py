from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File
from django.core.mail import send_mail
from django.conf import settings

class MembershipType(models.TextChoices):
    STUDENT = 'Student', _('Student')
    FACULTY = 'Faculty', _('Faculty')
    GENERAL = 'General', _('General')

class PlanType(models.TextChoices):
    ANNUAL = 'Annual', _('Annual')
    SEMI_ANNUAL = 'Semi-Annual', _('Semi-Annual')

class Member(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='member_profile'
    )
    name = models.CharField(max_length=100,null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$')])
    address = models.TextField()
    membership_type = models.CharField(max_length=10, choices=MembershipType.choices)
    plan_type = models.CharField(max_length=15, choices=PlanType.choices, blank=True)
    profile= models.ImageField(upload_to='profile_images/', blank=True, null=True)
    start_date = models.DateField(default=timezone.now)
    expiry_date = models.DateTimeField(default=timezone.now)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    is_verified_by_faculty = models.BooleanField(default=False)
    
    def is_active(self):
        return self.expiry_date and self.expiry_date.date() >= timezone.now().date()

    def __str__(self):
        return self.name or self.user.username
    

    def generate_qr_code(self):
        import qrcode
        from io import BytesIO
        from django.core.files import File

        data = f"Name: {self.name}\nPlan: {self.plan_type}\nExpiry: {self.expiry_date.strftime('%Y-%m-%d')}"
        qr = qrcode.make(data)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        file_name = f"{self.user.username}_qr.png"
        self.qr_code.save(file_name, File(buffer), save=False)
    
    def save(self, *args, **kwargs):
        if self.user.role == 'member':
            self.generate_qr_code()
        super().save(*args, **kwargs)
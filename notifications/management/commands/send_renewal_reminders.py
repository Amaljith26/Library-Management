from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils.timezone import now
from memberships.models import Member
from datetime import timedelta

class Command(BaseCommand):
    help = "Send renewal reminders to members whose memberships expire in 5 days."

    def handle(self, *args, **kwargs):
        reminder_date = now().date() + timedelta(days=5)

        members = Member.objects.filter(
            expiry_date__date=reminder_date,
            is_verified_by_faculty=True
        )

        if not members:
            self.stdout.write(self.style.WARNING("No members found with expiry in 5 days."))
            return

        for member in members:
            user = member.user
            if user.email:
                send_mail(
                    subject="Membership Renewal Reminder",
                    message=(
                        f"Dear {user.get_full_name() or user.username},\n\n"
                        f"Your membership will expire on {member.expiry_date.date()}. "
                        "Please renew it before the expiry to avoid service interruption.\n\n"
                        "Best regards,\nLibrary Team"
                    ),
                    from_email="noreply@library.com",
                    recipient_list=[user.email],
                    fail_silently=False
                )
                self.stdout.write(self.style.SUCCESS(f"Reminder sent to {user.email}"))

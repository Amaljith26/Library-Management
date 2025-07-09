from django.db import models
from users.models import User
from django.conf import settings
from django.db.models import Avg

class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('checked_out', 'Checked Out'),
        ('damaged', 'Damaged'),
        ('lost', 'Lost'),
    ]

    isbn = models.CharField(max_length=13, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    edition = models.CharField(max_length=50, blank=True)
    genre = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    tags = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    stock = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.title} ({self.isbn})"
    
    def average_rating(self):
        from feedback.models import Review  # avoid circular import
        avg = Review.objects.filter(book=self).aggregate(Avg('rating'))['rating__avg']
        return round(avg or 0, 1)



class FavoriteBook(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"


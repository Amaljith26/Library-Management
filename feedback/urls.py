from django.urls import path
from . import views
from .views import add_review


urlpatterns = [
    path('review/<int:book_id>/', views.add_review, name='add_review'),
]

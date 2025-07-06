from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Feedback

class FeedbackCreateView(CreateView):
    model = Feedback
    template_name = 'feedback.html'
    fields = ['user', 'book', 'rating', 'comment']
    success_url = reverse_lazy('dashboard')

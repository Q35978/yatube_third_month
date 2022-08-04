# users/views.py
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationFrom


class SingUp(CreateView):
    form_class = CreationFrom
    success_url = reverse_lazy('posts:index')
    template_name = 'users/singup.html'

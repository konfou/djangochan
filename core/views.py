import hashlib
from random import randint

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin

from .models import Board, Post
from .forms import NewThreadForm, NewReplyForm


class IndexView(ListView):
    model = Board
    template_name = 'core/index.html'
    context_object_name = 'boards'

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        threads = Post.objects.filter(
            thread__isnull=True).order_by('-bump')[:5]
        context['posts'] = {thread: thread.post_set.order_by(
            '-timestamp')[:3][::-1] for thread in threads}
        return context

class BoardView(FormMixin, DetailView):
    model = Board
    template_name = 'core/board.html'
    context_object_name = 'board'
    slug_field = 'ln'
    slug_url_kwarg = 'board'
    form_class = NewThreadForm

    def get_context_data(self, *args, **kwargs):
        context = super(BoardView, self).get_context_data(*args, **kwargs)
        board = kwargs['object']
        threads = board.post_set.filter(thread__isnull=True).order_by('-bump')
        context['posts'] = {thread: thread.post_set.order_by(
            '-timestamp')[:3][::-1] for thread in threads}
        return context

    def get_success_url(self):
        return reverse('thread', kwargs={'board': self.object.ln, 'thread': Post.objects.latest('pk').pk})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        form.instance.board = Board.objects.get(ln=kwargs['board'])
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        if '#' in form.instance.author:
            usr, pwd = form.instance.author.rsplit('#')
            hashpwd = hashlib.sha256(pwd.encode('utf-8')).hexdigest()[:10]
            form.instance.author = usr
            form.instance.tripcode = hashpwd

        form.save()
        return super().form_valid(form)

class ThreadView(FormMixin, DetailView):
    model = Post
    context_object_name = 'thread'
    template_name = 'core/thread.html'
    pk_url_kwarg = 'thread'
    form_class = NewReplyForm

    def get_context_data(self, *args, **kwargs):
        context = super(ThreadView, self).get_context_data(*args, **kwargs)
        thread = kwargs['object']
        context['board'] = thread.board
        context['replies'] = thread.post_set.order_by('timestamp')
        return context

    def get_success_url(self):
        return reverse('thread', kwargs={'board': self.object.board, 'thread': self.object.pk})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        form.instance.board = Board.objects.get(ln=kwargs['board'])
        form.instance.thread = Post.objects.get(pk=kwargs['thread'])
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        if '#' in form.instance.author:
            usr, pwd = form.instance.author.rsplit('#')
            hashpwd = hashlib.sha256(pwd.encode('utf-8')).hexdigest()[:10]
            form.instance.author = usr
            form.instance.tripcode = hashpwd

        form.save()
        return super().form_valid(form)

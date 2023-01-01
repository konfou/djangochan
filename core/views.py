from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin
from random import randint

from .models import Board, Post
from .forms import NewThreadForm, NewReplyForm


class IndexView(ListView):
    model = Board
    template_name = 'core/index.html'
    context_object_name = 'boards'

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
        context['threads'] = board.post_set.filter(thread__isnull=True).order_by('-bump')
        return context

    # TODO: Utilize Django's forms
    def post(self, request, *args, **kwargs):
        data = request.POST
        if int(data['verification']) == 4:
            new_post = Post()
            new_post.board = Board.objects.get(ln=kwargs['board'])
            new_post.author = data['author']
            new_post.text = data['text']
            new_post.save()

            return HttpResponseRedirect(reverse('thread', kwargs={'board': kwargs['board'], 'thread': new_post.pk}))

        return HttpResponseRedirect(reverse('board', kwargs={'board': kwargs['board']}))

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
        context['posts'] = thread.post_set.order_by('-timestamp')
        return context

    # TODO: Utilize Django's forms
    def post(self, request, *args, **kwargs):
        data = request.POST
        if int(data['verification']) == 4:
            new_post = Post()
            new_post.board = Board.objects.get(ln=kwargs['board'])
            new_post.thread = Post.objects.get(pk=kwargs['thread'])
            new_post.author = data['author']
            new_post.text = data['text']
            new_post.save()

        return HttpResponseRedirect(reverse('thread', kwargs={'board': kwargs['board'], 'thread': kwargs['thread']}))

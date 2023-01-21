from itertools import islice

from django.core.exceptions import ValidationError
from django.db.models import Q, Case, When
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin, DeleteView

from core.models import Board, Post
from .forms import NewThreadForm, NewReplyForm, ReportPostForm


class IndexView(ListView):
    model = Board
    template_name = 'boards/index.html'
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
    template_name = 'boards/board.html'
    context_object_name = 'board'
    slug_field = 'ln'
    slug_url_kwarg = 'board'
    form_class = NewThreadForm

    def get_context_data(self, *args, **kwargs):
        context = super(BoardView, self).get_context_data(*args, **kwargs)
        threads = self.object.post_set.filter(
            thread__isnull=True, archived=False).order_by(Case(When(sticky=True, then=0), default=1), '-bump')
        context['posts'] = {thread: thread.post_set.order_by(
            '-timestamp')[:3][::-1] for thread in threads}
        return context

    def get_success_url(self):
        # options is list that contains a string that has space separated keywords
        opts = self.request.POST.getlist('options')
        if opts != '':
            # doing it this way in case other options are added
            opts = opts[0].split()
            if 'nanako' in opts:
                return self.object.get_absolute_url()
        # else
        return Post.objects.last().get_absolute_url()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        form.instance.board = self.object
        if not request.session.session_key:
            request.session.create()
        form.instance.cookie = request.session.session_key
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class BoardCatalogView(BoardView):
    template_name = 'boards/catalog.html'

    def chunk(self, it, size):
        it = iter(it)
        return iter(lambda: tuple(islice(it, size)), ())

    # FIX: this should be done dynamically in template
    def get_context_data(self, *args, **kwargs):
        context = super(BoardCatalogView, self).get_context_data(
            *args, **kwargs)
        threads = self.object.post_set.filter(
            thread__isnull=True, archived=False).order_by('-bump')
        context['threads'] = list(self.chunk(threads, 5))
        return context


class BoardArchiveView(DetailView):
    # or ListView for model Post?
    model = Board
    template_name = 'boards/archive.html'
    context_object_name = 'board'
    slug_field = 'ln'
    slug_url_kwarg = 'board'

    def get_context_data(self, *args, **kwargs):
        context = super(BoardArchiveView, self).get_context_data(
            *args, **kwargs)
        # only threads can be archived so no need to check if thread
        context['threads'] = self.object.post_set.filter(
            archived=True).order_by('-bump')
        return context


class BoardSearchView(ListView):
    model = Post
    template_name = 'boards/search.html'
    context_object_name = 'results'

    def get_context_data(self, *args, **kwargs):
        context = super(BoardSearchView, self).get_context_data(
            *args, **kwargs)
        context['board'] = Board.objects.get(ln=self.kwargs['board'])
        return context

    def get_queryset(self):
        query = self.request.GET.get('q')
        board = Board.objects.get(ln=self.kwargs['board'])
        if query is None:
            return Post.objects.none()
        else:
            terms = query.split()
            # keyword argument queries are "and"d together
            return Post.objects.filter(board=board).filter(
                *(Q(subject__icontains=x) |
                  Q(text__icontains=x) |
                  Q(filename__icontains=x) for x in terms)
            ).order_by('-timestamp')


class ThreadView(FormMixin, DetailView):
    model = Post
    template_name = 'boards/thread.html'
    context_object_name = 'thread'
    pk_url_kwarg = 'thread'
    form_class = NewReplyForm

    def get_success_url(self):
        # options is list that contains a string that has space separated keywords
        opts = self.request.POST.getlist('options')
        if opts != '':
            # doing it this way in case other options are added
            opts = opts[0].split()
            if 'nanako' in opts:
                return self.object.board.get_absolute_url()
        # else
        return Post.objects.last().get_absolute_url()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        form.instance.board = self.object.board
        form.instance.thread = self.object
        if not request.session.session_key:
            request.session.create()
        form.instance.cookie = request.session.session_key
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # options contains a string that has space separated keywords
        # if no options were provided is None
        opts = form.cleaned_data['options'].split()
        form.save(opts=opts)
        return super().form_valid(form)


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'sys/delete.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post'

    def get_context_data(self, *args, **kwargs):
        context = super(PostDeleteView, self).get_context_data(*args, **kwargs)
        if not self.object.cookie:
            context['error'] = 'Post has no cookie attached.'
        elif self.object.cookie != self.request.session.session_key:
            context['error'] = 'Post was made in another session.'
        return context

    def get_success_url(self, post_pk):
        if self.object.thread:
            posts = self.object.thread.post_set.order_by('timestamp')
            indx = posts.filter(pk__lt=post_pk).count()
            if indx == 0:
                # no more replies in thread
                return self.object.thread.get_absolute_url()
            else:
                # previous reply to one deleted
                return posts[indx - 1].get_absolute_url()
        else:
            return self.object.board.get_absolute_url()

    def form_valid(self, form):
        # for certainty, otherwise no form exists if this doesn't hold
        if self.object.cookie == self.request.session.session_key:
            post_pk = self.object.pk
            self.object.delete()
            return HttpResponseRedirect(self.get_success_url(post_pk))


class PostReportView(FormMixin, DetailView):
    model = Post
    template_name = 'sys/report.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post'
    form_class = ReportPostForm

    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        form.instance.board = self.object.board
        form.instance.post = self.object
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

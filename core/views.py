from django.core.exceptions import ValidationError
from django.db.models import Case, When
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
        threads = self.object.post_set.filter(
            thread__isnull=True).order_by(Case(When(sticky=True, then=0), default=1), '-bump')
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
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class ThreadView(FormMixin, DetailView):
    model = Post
    template_name = 'core/thread.html'
    context_object_name = 'thread'
    pk_url_kwarg = 'thread'
    form_class = NewReplyForm

    def get_context_data(self, *args, **kwargs):
        context = super(ThreadView, self).get_context_data(*args, **kwargs)
        context['board'] = self.object.board
        context['replies'] = self.object.post_set.order_by('timestamp')
        return context

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
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # options contains a string that has space separated keywords
        # if no options were provided is None
        opts = str(form.cleaned_data['options'] or '').split()

        if self.object.post_set.count() > self.object.board.thread_bump_limit:
            opts.append('sage')

        form.save(opts=opts)
        return super().form_valid(form)

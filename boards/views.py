from django.core.exceptions import ValidationError
from django.db.models import Case, When
from django.http import HttpResponseRedirect
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


class ThreadView(FormMixin, DetailView):
    model = Post
    template_name = 'boards/thread.html'
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
    template_name = 'boards/sys/delete.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post'

    def get_context_data(self, *args, **kwargs):
        context = super(PostDeleteView, self).get_context_data(*args, **kwargs)
        return context

    def get_success_url(self, post_pk):
        if self.object.thread:
            posts = self.object.thread.post_set.order_by('timestamp')
            indx = posts.filter(pk__lt=post_pk).count()
            if indx == 0:
                return self.object.thread.get_absolute_url()
            else:
                return posts[indx - 1].get_absolute_url()
        else:
            return self.object.board.get_absolute_url()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        if not self.object.cookie:
            raise ValidationError('Post has no key attached.')
        elif self.object.cookie == self.request.session.session_key:
            post_pk = self.object.pk
            self.object.delete()
            return HttpResponseRedirect(self.get_success_url(post_pk))
        else:
            raise ValidationError('Post was made in another session.')


class PostReportView(FormMixin, DetailView):
    model = Post
    template_name = 'boards/sys/report.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post'
    form_class = ReportPostForm

    def get_context_data(self, *args, **kwargs):
        context = super(PostReportView, self).get_context_data(*args, **kwargs)
        return context

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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from datetime import datetime
from .models import Post, Comment
from django.urls import reverse_lazy
from .forms import PostForm, CommentForm
from .filters import PostFilter, CommentsFilterForm
from .tasks import comment_send_email, comment_accept_send_email


class PList(ListView):
    model = Post
    ordering = '-time_in'
    template_name = 'board.html'
    context_object_name = 'board'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_sale'] = None
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Comment.objects.filter(author_id=self.request.user.id).filter(post_id=self.kwargs.get('pk')):
            context['comment'] = "Откликнулся"
        elif self.request.user == Post.objects.get(pk=self.kwargs.get('pk')).author:
            context['comment'] = "Мое_объявление"
        return context


class PSearchList(ListView):
    model = Post
    ordering = '-time_in'
    template_name = 'search.html'
    context_object_name = 'search'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['filterset'] = self.filterset
        return context


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('ABoard.add_post',
                           'ABoard.change_post')
    form_class = PostForm
    model = Post
    template_name = 'create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = User.objects.get(id=self.request.user.id)
        post.save()
        return redirect(f'/board/{post.id}')


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('ABoard.add_post',
                           'ABoard.change_post')
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def dispatch(self, request, *args, **kwargs):
        author = Post.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("Редактировать объявление может только автор")


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('ABoard.add_post',
                           'ABoard.change_post')
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_search')

    def dispatch(self, request, *args, **kwargs):
        author = Post.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("Удалить объявление может только автор")


title = str("")


class Comments(PermissionRequiredMixin, ListView):
    permission_required = ('ABoard.add_comment',
                           'ABoard.change_comment')
    model = Comment
    template_name = 'comments.html'
    context_object_name = 'comments'

    def get_context_data(self, **kwargs):
        context = super(Comments, self).get_context_data(**kwargs)
        global title
        if self.kwargs.get('pk') and Post.objects.filter(id=self.kwargs.get('pk')).exists():
            title = str(Post.objects.get(id=self.kwargs.get('pk')).title)
            print(title)
        context['form'] = CommentsFilterForm(self.request.user, initial={'title': title})
        context['title'] = title
        if title:
            post_id = Post.objects.get(title=title)
            context['filter_comments'] = list(Comment.objects.filter(post_id=post_id).order_by('-created'))
            context['comment_post_id'] = post_id.id
        else:
            context['filter_comments'] = list(Comment.objects.filter(post_id__author_id=self.request.user).order_by('-created'))
        context['mycomments'] = list(Comment.objects.filter(author_id=self.request.user).order_by('-created'))
        return context

    def post(self, request, *args, **kwargs):
        global title
        title = self.request.POST.get('title')
        if self.kwargs.get('pk'):
            return HttpResponseRedirect('/comments')
        return self.get(request, *args, **kwargs)


@login_required
def comment_accept(request, **kwargs):
    if request.user.is_authenticated:
        comment = Comment.objects.get(id=kwargs.get('pk'))
        comment.active = True
        comment.save()
        comment_accept_send_email.delay(comment_id=comment.id)
        return HttpResponseRedirect('/comments')
    else:
        return HttpResponseRedirect('/accounts/login')


@login_required
def comment_delete(request, **kwargs):
    if request.user.is_authenticated:
        comment = Comment.objects.get(id=kwargs.get('pk'))
        comment.delete()
        return HttpResponseRedirect('/comments')
    else:
        return HttpResponseRedirect('/accounts/login')


class CommentPost(PermissionRequiredMixin, CreateView):
    permission_required = ('ABoard.add_comment',
                           'ABoard.change_comment')
    model = Comment
    template_name = 'comment.html'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = User.objects.get(id=self.request.user.id)
        comment.post = Post.objects.get(id=self.kwargs.get('pk'))
        comment.save()
        comment_send_email.delay(comment_id=comment.id)
        return redirect(f'/board/{self.kwargs.get("pk")}')
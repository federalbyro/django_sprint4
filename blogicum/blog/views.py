# blog/views.py
from django.http import Http404
from django.views.generic import (
    DetailView, ListView, CreateView, UpdateView, DeleteView)
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, get_user_model
from django.db.models import Count

from .models import Post, Category, Comment
from .forms import CommentForm
from .mixin import (PostVisibilityMixin,
                    AuthorRequiredMixin,
                    SinglePostObjectMixin,
                    SingleCommentObjectMixin)

User = get_user_model()

showing = ['title', 'text', 'category', 'location',
           'pub_date', 'is_published', 'image']


class Index(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.filter(
                is_published=True,
                pub_date__lte=now(),
                category__is_published=True
            )
            .select_related('category', 'author', 'location')
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )


class PostDetail(PostVisibilityMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if not self.check_post_visibility(post, self.request.user):
            raise Http404("Публикация не найдена.")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context['post']
        context['comments'] = post.comments.all()
        context['comments_count'] = post.comments.count()
        if self.request.user.is_authenticated:
            context['form'] = CommentForm()
        return context


class CategoryPosts(ListView):
    model = Category
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True
        )
        return self.category.posts.filter(
            is_published=True,
            pub_date__lte=now()
        ).select_related('category', 'author', 'location')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'page_obj'
    paginate_by = 10

    def get_queryset(self):
        self.profile = get_object_or_404(
            User, username=self.kwargs['username'])
        queryset = Post.objects.filter(author=self.profile).select_related(
            'category', 'author', 'location')
        if self.request.user != self.profile:
            queryset = queryset.filter(is_published=True, pub_date__lte=now())
        return (queryset.annotate(comment_count=Count('comments')).
                order_by('-pub_date'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context


class CreatePost(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    fields = showing

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class EditPost(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    fields = showing

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.object.pk})

    def handle_no_permission(self):
        post = self.get_object()
        return redirect('blog:post_detail', pk=post.pk)


class RegistrationView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.username})

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        if user:
            login(self.request, user)
        return response


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['username', 'first_name', 'last_name', 'email']

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.username})


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/add_comment.html'

    def form_valid(self, form):
        post_id = self.kwargs.get('pk')
        post = get_object_or_404(Post, pk=post_id)
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.object.post.pk})


class EditCommentView(LoginRequiredMixin,
                      AuthorRequiredMixin,
                      SingleCommentObjectMixin,
                      UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.object.post.pk})


class DeletePostView(LoginRequiredMixin,
                     AuthorRequiredMixin,
                     SinglePostObjectMixin,
                     DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class DeleteCommentView(LoginRequiredMixin,
                        AuthorRequiredMixin,
                        SingleCommentObjectMixin,
                        DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.object.post.pk})

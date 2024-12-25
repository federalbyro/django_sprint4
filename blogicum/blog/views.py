# blog/views.py
from django.http import Http404
from django.views.generic import (
    DetailView, ListView, CreateView, UpdateView, DeleteView
)
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, get_user_model
from django.db.models import Count

from .models import Post, Category, Comment
from .forms import CommentForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .mixin import (
    PostVisibilityMixin,
    AuthorRequiredMixin,
    SinglePostObjectMixin,
    SingleCommentObjectMixin
)

User = get_user_model()

# Поля, отображаемые при создании и редактировании публикации
SHOWING_FIELDS = [
    'title', 'text', 'category', 'location',
    'pub_date', 'is_published', 'image'
]


def get_paginated_page(request, queryset, per_page=10):
    """
    Возвращает объект страницы с пагинацией.
    
    :param request: HttpRequest объект.
    :param queryset: QuerySet для пагинации.
    :param per_page: Количество объектов на странице.
    :return: Объект Page.
    """
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page')
    try:
        paginated_page = paginator.page(page)
    except PageNotAnInteger:
        paginated_page = paginator.page(1)
    except EmptyPage:
        paginated_page = paginator.page(paginator.num_pages)
    return paginated_page


def annotate_comment_count(queryset):
    """
    Аннотирует переданный QuerySet количеством комментариев для каждого поста.
    """
    return queryset.annotate(comment_count=Count('comments'))


class Index(ListView):
    """Главная страница блога с списком опубликованных публикаций."""
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10  # Эта строка теперь не обязательна, так как пагинация обрабатывается функцией

    def get_queryset(self):
        """
        Получает опубликованные публикации 
        с предварительной выборкой связанных объектов.
        """
        queryset = Post.objects.filter(
            is_published=True,
            pub_date__lte=now(),
            category__is_published=True
        ).select_related('category', 'author', 'location').order_by('-pub_date')
        
        return annotate_comment_count(queryset)
    
    def get_context_data(self, **kwargs):
        """
        Добавляет пагинированный набор постов в контекст.
        """
        context = super().get_context_data(**kwargs)
        context['page_obj'] = get_paginated_page(self.request, self.get_queryset(), self.paginate_by)
        return context


class PostDetail(PostVisibilityMixin, DetailView):
    """Детальная страница публикации с комментариями."""
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_pk'  # Соответствует параметру из URL

    def get_object(self, queryset=None):
        """
        Получает объект публикации и проверяет его доступность.
        Использует get_object_or_404() внутри DetailView.
        """
        post = super().get_object(queryset)
        if not self.check_post_visibility(post, self.request.user):
            raise Http404("Публикация не найдена.")
        return post

    def get_context_data(self, **kwargs):
        """
        Добавляет комментарии и форму комментария в контекст.
        """
        context = super().get_context_data(**kwargs)
        post = context['post']
        context['comments'] = post.comments.all()
        context['comments_count'] = post.comments.count()
        if self.request.user.is_authenticated:
            context['form'] = CommentForm()
        return context


class CategoryPosts(ListView):
    """Страница со списком публикаций по выбранной категории."""
    model = Category
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        queryset = self.category.posts.filter(
            is_published=True,
            pub_date__lte=now()
        ).select_related('category', 'author', 'location').order_by('-pub_date')

        return annotate_comment_count(queryset)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['page_obj'] = get_paginated_page(self.request, self.get_queryset(), self.paginate_by)
        return context


class ProfileView(ListView):
    """Профиль пользователя с его публикациями."""
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'page_obj'
    paginate_by = 10

    def get_queryset(self):
        self.profile = get_object_or_404(
            User, username=self.kwargs['username']
        )
        queryset = Post.objects.filter(author=self.profile).select_related(
            'category', 'author', 'location'
        )
        if self.request.user != self.profile:
            queryset = queryset.filter(is_published=True, pub_date__lte=now())

        return annotate_comment_count(queryset).order_by('-pub_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        context['page_obj'] = get_paginated_page(self.request, self.get_queryset(), self.paginate_by)
        return context

class CreatePost(LoginRequiredMixin, CreateView):
    """Создание новой публикации."""
    model = Post
    template_name = 'blog/create.html'
    fields = SHOWING_FIELDS

    def form_valid(self, form):
        """
        Устанавливает автора публикации перед сохранением формы.
        """
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """
        Перенаправление на профиль 
        пользователя после успешного создания публикации.
        """
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class EditPost(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    """Редактирование существующей публикации."""
    model = Post
    template_name = 'blog/create.html'
    fields = SHOWING_FIELDS
    pk_url_kwarg = 'post_pk'  # Соответствует параметру из URL

    def get_success_url(self):
        """
        Перенаправление на детальную страницу публикации 
        после успешного редактирования.
        """
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_pk': self.object.pk})

    def handle_no_permission(self):
        """
        Обработка ситуации, когда пользователь 
        не имеет прав на редактирование публикации.
        """
        post = self.get_object()
        return redirect('blog:post_detail', post_pk=post.pk)


class RegistrationView(CreateView):
    """Регистрация нового пользователя."""
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm

    def get_success_url(self):
        """
        Перенаправление на профиль пользователя после успешной регистрации.
        """
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.username})

    def form_valid(self, form):
        """
        Регистрация пользователя и автоматический 
        вход после успешной регистрации.
        """
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        if user:
            login(self.request, user)
        return response


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля текущего пользователя."""
    model = User
    template_name = 'blog/user.html'
    fields = ['username', 'first_name', 'last_name', 'email']

    def get_object(self, queryset=None):
        """
        Возвращает объект текущего пользователя для редактирования.
        """
        return self.request.user

    def get_success_url(self):
        """
        Перенаправление на профиль пользователя после успешного редактирования.
        """
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.username})


class AddCommentView(LoginRequiredMixin, CreateView):
    """Добавление нового комментария к публикации."""
    model = Comment
    form_class = CommentForm
    template_name = 'blog/add_comment.html'

    def form_valid(self, form):
        """
        Устанавливает автора комментария и связывает его 
        с соответствующей публикацией.
        Использует get_object_or_404() для извлечения публикации.
        """
        post_pk = self.kwargs.get('post_pk')  # Соответствует параметру из URL
        post = get_object_or_404(Post, pk=post_pk)
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        """
        Перенаправление на детальную страницу 
        публикации после успешного добавления комментария.
        """
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_pk': self.object.post.pk})


class EditCommentView(LoginRequiredMixin,
                      AuthorRequiredMixin,
                      SingleCommentObjectMixin,
                      UpdateView):
    """Редактирование существующего комментария."""
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_pk'  # Соответствует параметру из URL

    def get_success_url(self):
        """
        Перенаправление на детальную страницу 
        публикации после успешного редактирования комментария.
        """
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_pk': self.object.post.pk})


class DeletePostView(LoginRequiredMixin,
                     AuthorRequiredMixin,
                     SinglePostObjectMixin,
                     DeleteView):
    """Удаление существующей публикации."""
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_pk'  # Соответствует параметру из URL

    def get_success_url(self):
        """
        Перенаправление на профиль 
        пользователя после успешного удаления публикации.
        """
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class DeleteCommentView(LoginRequiredMixin,
                        AuthorRequiredMixin,
                        SingleCommentObjectMixin,
                        DeleteView):
    """Удаление существующего комментария."""
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_pk'  # Соответствует параметру из URL

    def get_success_url(self):
        """
        Перенаправление на детальную страницу
        публикации после успешного удаления комментария.
        """
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_pk': self.object.post.pk})

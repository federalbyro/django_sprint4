from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),  # Главная страница блога
    path(
        'posts/<int:post_pk>/',
        views.PostDetail.as_view(),
        name='post_detail'
    ),  # Детальная страница публикации с идентификатором post_pk
    path(
        'category/<slug:category_slug>/',
        views.CategoryPosts.as_view(),
        name='category_posts'
    ),  # Список публикаций по категории с использованием category_slug
    path(
        'posts/create/',
        views.CreatePost.as_view(),
        name='create_post'
    ),  # Страница создания новой публикации
    path(
        'posts/<int:post_pk>/edit/',
        views.EditPost.as_view(),
        name='edit_post'
    ),  # Страница редактирования публикации с идентификатором post_pk
    path(
        'profile/<str:username>/',
        views.ProfileView.as_view(),
        name='profile'
    ),  # Профиль пользователя по его username
    path(
        'edit_profile/',
        views.EditProfileView.as_view(),
        name='edit_profile'
    ),  # Страница редактирования профиля текущего пользователя
    path(
        'posts/<int:post_pk>/comment/',
        views.AddCommentView.as_view(),
        name='add_comment'
    ),  # Добавление комментария к публикации с идентификатором post_pk
    path(
        'posts/<int:post_pk>/edit_comment/<int:comment_pk>/',
        views.EditCommentView.as_view(),
        name='edit_comment'
    ),  # Редактирование комментария с идентификаторами post_pk и comment_pk
    path(
        'posts/<int:post_pk>/delete/',
        views.DeletePostView.as_view(),
        name='delete_post'
    ),  # Удаление публикации с идентификатором post_pk
    path(
        'posts/<int:post_pk>/delete_comment/<int:comment_pk>/',
        views.DeleteCommentView.as_view(),
        name='delete_comment'
    ),  # Удаление комментария с идентификаторами post_pk и comment_pk
]

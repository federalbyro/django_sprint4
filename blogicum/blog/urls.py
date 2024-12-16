from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetail.as_view(), name='post_detail'),
    path('category/<slug:category_slug>/',
         views.CategoryPosts.as_view(), name='category_posts'),
    path('posts/create/', views.CreatePost.as_view(), name='create_post'),
    path('posts/<int:pk>/edit/', views.EditPost.as_view(),
         name='edit_post'),  # Исправлено имя и параметр
    path('profile/<str:username>/',
         views.ProfileView.as_view(), name='profile'),
    # Маршрут редактирования профиля
    path('edit_profile/', views.EditProfileView.as_view(),
         name='edit_profile'),
    path('posts/<int:pk>/comment/',
         views.AddCommentView.as_view(), name='add_comment'),
    path('posts/<int:pk>/edit_comment/<int:comment_id>/',
         views.EditCommentView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete/',
         views.DeletePostView.as_view(), name='delete_post'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.DeleteCommentView.as_view(), name='delete_comment'),
]

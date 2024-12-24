from django.contrib import admin
from .models import Category, Location, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ-класс для модели Category."""
    list_display = ('title', 'slug', 'is_published', 'created_at')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Админ-класс для модели Location."""
    list_display = ('name', 'is_published', 'created_at')
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Админ-класс для модели Post."""
    list_display = ('title', 'author', 'category', 'pub_date', 'is_published')
    list_filter = ('is_published', 'category', 'pub_date')
    search_fields = ('title', 'text')
    date_hierarchy = 'pub_date'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админ-класс для модели Comment."""
    list_display = ('author', 'post', 'created_at')
    search_fields = ('author__username', 'text')

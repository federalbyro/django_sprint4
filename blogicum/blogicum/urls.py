from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from blog import views

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
handler403 = 'pages.views.csrf_failure'

urlpatterns = [
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', views.RegistrationView.as_view(),
         name='registration'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

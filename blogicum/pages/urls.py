from django.urls import path
from . import views

app_name = 'pages'

handler403 = 'pages.views.csrf_failure'
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

urlpatterns = [
    path('about/', views.HomePage.as_view(), name='about'),
    path('rules/', views.RulesPage.as_view(), name='rules'),
]

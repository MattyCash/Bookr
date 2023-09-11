from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.post_list, name='post_list'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_pk>/comments/new/', views.comment_edit, name='comment_create'),
    path('posts/<int:post_pk>/comments/<int:comment_pk>/', views.comment_edit, name='comment_edit'),
    path('posts/<int:pk>/media/', views.post_media, name='post_media'),
    path('publishers/<int:pk>/', views.publisher_edit, name='publisher_detail'),
    path('publishers/new/', views.publisher_edit, name='publisher_create')
]
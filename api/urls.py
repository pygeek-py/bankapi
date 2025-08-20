from django.urls import path
from . import views
from .views import UserListView

urlpatterns = [
    path('blogposts/', views.BlogPostListCreate.as_view(), name='blogpost-list-create'),
    path('blogposts/<int:pk>/', views.BlogPostRetriveUpdateDestroy.as_view(), name='update'),
    path('blogposts/list/', views.BlogPostList.as_view(), name='blogpost-list'),
    path('users/', UserListView.as_view(), name='user-list'),
]

from django.urls import path
from . import views
from .views import EmailVerificationView

urlpatterns = [
    path('blogposts/', views.BlogPostListCreate.as_view(), name='blogpost-list-create'),
    path('blogposts/<int:pk>/', views.BlogPostRetriveUpdateDestroy.as_view(), name='update'),
    path('blogposts/list/', views.BlogPostList.as_view(), name='blogpost-list'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('account/inactive/', views.account_inactive, name='account_inactive'),
    path('withdraw/', views.withdraw_view, name='withdraw'),
    path('transfer/', views.transfer_view, name='transfer'),
    path('get-balance/', views.get_user_balances_view, name='get-balance'),
]
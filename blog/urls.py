from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Login and Logout
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True, template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='first'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('guest/', views.guest, name='guest'),
    path('', views.first, name='first'),

    # Books
    path('new_user/', views.new_user, name='new_user'),
    path('home/', views.home, name='home'),
    path('home/<int:pk>/', views.book_detail, name='book_detail'),
    #path('home/<int:pk>/comment/', views.add_comment_to_post, name='add_comment_to_post'),
    #path('comment/<int:pk>/approve/', views.comment_approve, name='comment_approve'),
    #path('comment/<int:pk>/remove/', views.comment_remove, name='comment_remove'),
    path('home/<int:pk>/book_like/', views.book_like, name='book_like'),
    path('home/<int:pk>/book_dislike/', views.book_dislike, name='book_dislike'),
]
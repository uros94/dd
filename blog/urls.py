from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .models import Profile

#remove old guest accounts
from background_task.models import Task
if not Task.objects.filter(verbose_name="remove_guests").exists():
   Profile.removeGuests(None, repeat=Task.DAILY, verbose_name="remove_guests", repeat_until=None)
#Profile.removeGuests(None, repeat=60000, repeat_until=None)

urlpatterns = [
    # Login and Logout
    #path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True, template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='first'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('guest/', views.guest, name='guest'),
    path('', views.first, name='first'),

    # Books
    path('terminal/', views.terminal, name='terminal'),
    path('home/', views.home, name='home'),
    path('home/<int:pk>/', views.book_detail, name='book_detail'),
    path('home/<int:pk>/book_like/', views.book_like, name='book_like'),
    path('home/<int:pk>/book_dislike/', views.book_dislike, name='book_dislike'),

    path('test/', views.test, name='test'),
]
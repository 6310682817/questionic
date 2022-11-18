from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('signup', views.signup, name='signup'),
    path('<str:status>/<str:userf>', views.follow, name='follow'),
    path('<str:username>', views.userprofile, name='userprofile'),
]
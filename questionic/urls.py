from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'questionic'
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    
    path('post_question/', views.post_question, name='post_question'),
    path('question/<int:question_id>', views.question, name='question'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
app_name = 'questionic'
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('post_question/', views.post_question, name='post_question'),
    path('question/<int:question_id>', views.question, name='question'),
    path('notification/', views.notification, name='notification'),
    path('notification_alert/', views.notification_alert, name='notification_alert'),
    path('search/', views.search, name='search'),
    path('report/<str:type_report>/<int:report_id>', views.report, name='report'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
] 
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


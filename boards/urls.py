from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<slug:board>/', views.BoardView.as_view(), name='board'),
    path('<slug:board>/thread/<int:thread>/',
         views.ThreadView.as_view(), name='thread'),
    path('sys/post/<slug:board>/<int:post>/delete', views.PostDeleteView.as_view(), name='post-delete'),
    path('sys/post/<slug:board>/<int:post>/report', views.PostReportView.as_view(), name='post-report'),
]

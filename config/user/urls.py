from django.urls import path
from . import views


urlpatterns = [
    path('config/user/', views.UserConfigList.as_view()),
    path('config/user/<int:pk>/', views.UserConfigDetail.as_view()),
]
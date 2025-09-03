from django.urls import path
from . import views

urlpatterns = [
    path('buildings/', views.BuildingList.as_view()),
    path('buildings/choices/', views.BuildingExt.getList),
    path('buildings/<int:pk>/', views.BuildingDetail.as_view()),
    path('buildings/selection/', views.BuildingSelection.as_view()),

    path('floors/', views.FloorList.as_view()),
    path('floors/lightingstate/', views.FloorLightingState.as_view()),
    path('floors/<int:pk>/', views.FloorDetail.as_view()),
    path('floors/selection/', views.FloorSelection.as_view()),

    path('zones/', views.ZoneList.as_view()),
    path('zones/<int:pk>/', views.ZoneDetail.as_view()),
    path('zones/selection/', views.ZoneSelection.as_view()),

    path('doors/', views.DoorList.as_view()),
    path('doors/<int:pk>/', views.DoorDetail.as_view()),
    path('doors/selection/', views.DoorSelection.as_view()),
]

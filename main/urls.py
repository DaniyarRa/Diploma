from django.urls import path

from .views import main_view, crime_details
urlpatterns = [
    path("", main_view, name="main_view"),
    path('api/crime-details/', crime_details, name='crime_details'),
]
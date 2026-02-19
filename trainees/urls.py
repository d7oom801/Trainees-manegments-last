from django.urls import path
from .views import register_view
urlpatterns = [
    path('registration', register_view, name='registration')


]

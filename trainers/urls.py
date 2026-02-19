from django.contrib import admin
from django.urls import path, include
from trainees.views import end_training_view, register_view


urlpatterns = [
    path('end-training/<int:id>/', end_training_view, name='end_training_btn'),
    path('registration', register_view, name='registration'),
    path('', admin.site.urls),
]

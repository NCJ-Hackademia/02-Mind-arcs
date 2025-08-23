from django.urls import path
from .views import hello_api, root_api, upload_image

from . import views

urlpatterns = [
    path('', root_api),
    path('hello/', hello_api),
    
    path('upload-image/', views.upload_image, name='upload_image'),
    path('set-preference/', views.set_preference, name='set_preference'),
]
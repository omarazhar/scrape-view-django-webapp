from django.urls import path
from . import views
from .views import updates_handler, login_view, register_view, logout_view

urlpatterns = [
    path('', views.index, name="index"),
    path('updates/', updates_handler, name='updates_handler'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
]
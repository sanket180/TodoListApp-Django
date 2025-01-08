from django.urls import path
from . import views
urlpatterns = [
    path("login/",views.log_in,name="login"),
    path("register/",views.register, name="register"),
     path("user_logout/" ,views.user_logout,name='user_logout'),
]

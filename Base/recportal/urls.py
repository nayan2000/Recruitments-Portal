from django.conf.urls import url
from recportal import views

app_name = 'recportal'
urlpatterns = [
    url(r'^signin/$', views.SignIn, name='signin'),
    url(r'^signout/$', views.SignOut, name='signout'),
]

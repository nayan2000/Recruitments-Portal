from django.conf.urls import url
from recportal import views

app_name = 'recportal'
urlpatterns = [
    url(r'^signin/$', views.SignIn, name='signin'),
    url(r'^signout/$', views.SignOut, name='signout'),
    url(r'^home/$', views.Home, name='home'),
    url(r'^recommendations/$', views.Recommendations, name='recommendations'),
    url(r'^update-recommendations/$', views.UpdateRecommendations, name='updaterecommendations'),
    url(r'^my-candidates/$', views.MyCandidates, name='mycandidates'),
]

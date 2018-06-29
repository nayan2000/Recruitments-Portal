from django.conf.urls import url
from recportal import views

app_name = 'recportal'
urlpatterns = [
    url(r'^signin/$', views.SignIn, name='signin'),
    url(r'^signout/$', views.SignOut, name='signout'),
    url(r'^$', views.Home, name='home'),
    url(r'^recommendations/$', views.Recommendations, name='recommendations'),
    url(r'^my-candidates/$', views.MyCandidates, name='mycandidates'),
    url(r'^candidates/$', views.Candidates, name='candidates'),
    url(r'^profile/(?P<first_name>[A-Za-z_]+)-(?P<last_name>[A-Za-z]+)/$', views.CandidateProfile, name='profile'),
    url(r'^pitch/(?P<first_name>[A-Za-z_]+)-(?P<last_name>[A-Za-z]+)/$', views.PitchCandidate, name='pitch'),
    url(r'^recommend/(?P<first_name>[A-Za-z_]+)-(?P<last_name>[A-Za-z]+)/$', views.RecommendCandidate, name='recommend'),
    url(r'^my-pitches/$', views.MyPitches, name="mypitches"),
    url(r'^pitches/$', views.Pitches, name="pitches"),
    url(r'^download/(?P<filename>.+)/$', views.Download, name="download"),    
]

from django.conf.urls import include, url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'setup/assignperson/$', views.assignperson, name='assignperson'),

    url(r'setup/rock/$', views.rocksetup, name='rocksetup'),
    url(r'setup/$', views.setup, name='setup'),
    url(r'endsession/$', views.endsession, name='endsession'),
    url(r'session/$', views.session, name='session'),
    url(r'club/$', views.club, name='club'),
    url(r'club/add/$', views.addclub, name='addclub'),
    url(r'rfid/$', csrf_exempt(views.rfid), name='rfid'),


    url(r'shot1/$', csrf_exempt(views.shot1), name='shot1'),
    url(r'shot2/$', csrf_exempt(views.shot2), name='shot2'),
    #url(r'shot3/$', csrf_exempt(views.shot3), name='shot3'), # this will be used for the tee-tee time

    url(r'club/(?P<club_id>[0-9]+)/$', views.clubdetail, name='clubdetail'),
]


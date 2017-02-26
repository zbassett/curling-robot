from django.conf.urls import include, url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'setup/assignperson/$', views.assignperson, name='assignperson'),

    #url(r'setup/rock/$', views.rocksetup, name='rocksetup'),
    url(r'setup/$', views.setup, name='setup'),
    url(r'setup/assign_person/$', views.assignperson, name='assignperson'),
    url(r'setup/assign_rfid/$', views.assignrfid, name='assignrfid'),

    url(r'setup/assign_sht/$', views.assignrocks, name='assignrocks'),
    url(r'setup/assign_rock_rfid/$', views.assignrockrfid, name='assignrockrfid'),

    url(r'endsession/$', views.endsession, name='endsession'),
    url(r'session/$', views.session, name='session'),

    url(r'club/new/add_edit_club/$', views.addclub, name='addclub'), #post request to add
    url(r'club/new/$', views.addclub, name='addclub'),
    url(r'club/(?P<club_id>[0-9]+)/add_edit_club/$', views.editclub, name='editclub'), #post request to edit
    url(r'club/(?P<club_id>[0-9]+)/$', views.clubdetail, name='clubdetail'),
    url(r'club/$', views.club, name='club'),

    url(r'person/new/add_edit_person/$', views.addperson, name='addperson'), #post request to add
    url(r'person/new/$', views.addperson, name='addperson'),
    url(r'person/(?P<person_id>[0-9]+)/add_edit_person/$', views.editperson, name='editperson'), #post request to edit
    url(r'person/(?P<person_id>[0-9]+)/$', views.persondetail, name='persondetail'),
    url(r'person/$', views.person, name='person'),

    url(r'sheet/$', views.sheet, name='sheet'),


    url(r'rfid/$', csrf_exempt(views.rfid), name='rfid'),


    url(r'shot1/$', csrf_exempt(views.shot1), name='shot1'),
    url(r'shot2/$', csrf_exempt(views.shot2), name='shot2'),
    #url(r'shot3/$', csrf_exempt(views.shot3), name='shot3'), # this will be used for the tee-tee time


]


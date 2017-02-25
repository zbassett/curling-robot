from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import AssignPersonForm, AssignRFIDForm, AddClubForm, AssignRockForm, AssignRockRFIDForm

from .models import Club, Person, Session, SessionPerson, RFIDRawData, Shot, SessionRock
from .functions import DistanceCalc
from django.views.generic.edit import CreateView

import time, datetime

@login_required
def index(request):
    from django import forms
    class NameForm(forms.Form):
        your_name = forms.CharField(label='Your name', max_length=100)

    template = "curling/index.html"
    context = { "form" : NameForm() }
    return render( request, template, context )

@login_required
def assignperson(request):
    s = Session.objects.get_or_create(IsClosed=0)[0]
    s.IsSetup = 1
    s.save()

    if request.method == "POST":
        print(request.POST)
        form_class = AssignPersonForm(request.POST)
        if form_class.is_valid():
            p = SessionPerson(Person_id=request.POST['person_to_assign'], Session_id=s.id)
            p.save()
        form_RFID = AssignRFIDForm
    return setup(request)

@login_required
def assignrfid(request):
    s = Session.objects.get_or_create(IsClosed=0)[0]
    s.IsSetup = 1
    s.save()
    if request.method == "POST":
        form_RFID = AssignRFIDForm(request.POST)
        if form_RFID.is_valid():
            p = SessionPerson.objects.get(pk=request.POST['person_to_assign']) 
            p.RFID=RFIDRawData.objects.filter(id=request.POST['rfid_value']).values_list('RFIDValue',flat=True)[0]
            p.save()

            r = RFIDRawData.objects.all()
            r.delete()

        form_class = AssignPersonForm
    return setup(request)

@login_required
def setup(request):
    s = Session.objects.get_or_create(IsClosed=0)[0]
    s.IsSetup = 1
    s.save()

    form_class = AssignPersonForm
    form_RFID = AssignRFIDForm

    template = "curling/setup.html"
    context = {'form': form_class, 'formRFID': form_RFID}
    return render( request, template, context )

@login_required
def rocksetup(request):
    s = Session.objects.get_or_create(IsClosed=0)[0]
    #print('ROCKsetup')
    s.IsSetup = 1
    s.save()

    if request.method == "POST":
        print(request.POST)
        if 'add_rock' in request.POST:
            form_class = AssignRockForm(request.POST)
            if form_class.is_valid():
                p = SessionRock(Rock_id=request.POST['rock_to_assign'], Session_id=s.id)
                p.save()
            form_RFID = AssignRockRFIDForm
        elif 'assign_rfid' in request.POST:
            form_RFID = AssignRockRFIDForm(request.POST)
            if form_RFID.is_valid():
                p = SessionRock.objects.get(pk=request.POST['rock_to_assign']) 
                p.RFID=RFIDRawData.objects.filter(id=request.POST['rfid_value']).values_list('RFIDValue',flat=True)[0]
                p.save()

                r = RFIDRawData.objects.all()
                r.delete()

            form_class = AssignRockForm

    else:
        form_class = AssignRockForm
        form_RFID = AssignRockRFIDForm

    #form_class = AssignRockForm
    #form_RFID = AssignRockRFIDForm

    template = "curling/rocksetup.html"
    context = {'form': form_class, 'formRFID': form_RFID}
    return render( request, template, context )

@login_required
def session(request):
    s = Session.objects.get_or_create(IsClosed=0)[0]
    s.IsSetup = 0
    s.save()

    most_recent_shot = Shot.objects.filter(Session=s).order_by('-id')[:1]
    #if most_recent_shot.Shot.Person:
        #last_five_shots = Shot.objects.filter(Person=most_recent_shot.Person).order_by('-id')[:5]
    #else:
        #last_five_shots = most_recent_shot


    template = "curling/session.html"
    context = {'most_recent_shot': most_recent_shot}
    return render( request, template, context )

@login_required
def endsession(request):
    print('EndSessionRequest')
    s = Session.objects.all()
    #print('ROCKsetup')
    s.update(IsClosed = 1)

@login_required
def club(request):
    latest_club_list = Club.objects.order_by('Name')
    context = {'latest_club_list': latest_club_list}
    return render(request, 'curling/clublist.html', context)

@login_required
def addclub(request):
    if request.method == "POST":
        form_class = AddClubForm(request.POST)
        if form_class.is_valid():
            c = Club(Name=request.POST['club_name'],Country=request.POST['country_field'],Address1=request.POST['address1_field'],Address2=request.POST['address2_field'],City=request.POST['city_field'],State=request.POST['state_field'],Zip=request.POST['zip_field'])
            c.save()

            latest_club_list = Club.objects.order_by('Name')
            context = {'latest_club_list': latest_club_list}
            return redirect('curling/club/')
    else:
        form_class = AddClubForm()
        context = {'form': form_class}
        return render(request, 'curling/addclub.html', context)

@login_required
def clubdetail(request, club_id):
    model = get_object_or_404(Club.objects, pk = club_id)
    template_name = 'curling/clubdetail.html'
    context = {"model": model}
    return render( request, template_name, context )

def assignperson(request, person_id):
    model = get_object_or_404(Person.objects, pk = person_id)
    try:
	selected_person = Person.choice_set.get(pk=request.POST('choice'))
    except (KeyError, Person.DoesNotExist):
        # Redisplay the question voting form.
        # Redisplay the question voting form.
    	unused_person_list = Person.objects.order_by('FirstName')
    	template = "curling/setup.html"
    	context = {'unused_person_list': unused_person_list}
    	return render( request, template, context )
    else:
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

def rfid(request):
    unparsed_value = request.POST.get('payloadvalue')
    origin_node = unparsed_value[-1:]
    rfid_value = unparsed_value[4:-2]
    print(rfid_value)
    r = RFIDRawData(RFIDValue=rfid_value,SourceNode=origin_node)
    r.save()
    
    try:
        s = Session.objects.get(IsClosed=0,IsSetup=0)
        try:
            p = SessionPerson.objects.get(Session=s.id,RFID=rfid_value)
            sh, created = Shot.objects.get_or_create(IsComplete=0,Session_id=s.id,HasReceivedData=0)
            sh.Person_id=p.Person_id
            sh.save()

            r = Shot.objects.exclude(pk=sh.id)
            r.update(IsComplete = 1)

        except Exception as e:
            print(str(e))
            pass

        try:
            r = SessionRock.objects.get(Session=s.id,RFID=rfid_value)
            sh, created = Shot.objects.get_or_create(IsComplete=0,Session_id=s.id,HasReceivedData=0)
            sh.Rock_id=r.Rock_id
            sh.save()

            r = Shot.objects.exclude(pk=sh.id)
            r.update(IsComplete = 1)

        except Exception as e:
            print(str(e))
            pass
    except Session.DoesNotExist:
        print("NoActiveSessions")

    return  HttpResponse(rfid_value)

def shot1(request):
    unparsed_value = request.POST.get('payloadvalue')[6:]
    #print(unparsed_value)
    
    shotData = unparsed_value.split(",")

    # shotData[x]
    # 0: teeTripMasterTime
    # 1: teeTripDuration
    # 2: teeHogSplit
    # 3: hogTripDuration
    # 4: tempC
    # 5: humidity
    # 6: distance1
    # 7: distance2


    s = Session.objects.get(IsClosed=0,IsSetup=0)
    sh = Shot.objects.get(IsComplete=0,Session_id=s.id)
    sh.TeeTripMasterTime = datetime.datetime.fromtimestamp(float(shotData[0]))  #convert to datetime
    sh.TeeTripDuration = shotData[1]
    sh.TeeHogSplit= shotData[2]
    sh.HogTripDuration = shotData[3]
    sh.TempC = shotData[4]
    sh.Humidity = shotData[5]
    sh.TeePingTime = shotData[6]
    sh.HogPingTime1 = shotData[7]
	
    sh.HasReceivedData = 1

    sh.save()


    if sh.Rock:
    	rock_diameter = sh.Rock.Diameter
    else:
    	rock_diameter = 292.1  #using a default value of 11.5" (292.1mm)

    sh.HogSpeed = float(rock_diameter) / float(sh.HogTripDuration)
    sh.TeeSpeed = float(rock_diameter) / float(sh.TeeTripDuration)
    sh.AvgSplitSpeed = float(6.4008) / (float(sh.TeeHogSplit)/1000)  #tee-hog = 21 feet = 6.4008 meters
    sh.TeeDistance = DistanceCalc(sh.TeePingTime,sh.TempC,sh.Humidity)
    sh.HogDistance1 = DistanceCalc(sh.HogPingTime1,sh.TempC,sh.Humidity)


    sh.save()

    return  HttpResponse(unparsed_value)

def shot2(request):
    unparsed_value = request.POST.get('payloadvalue')[6:]

    s = Session.objects.get(IsClosed=0,IsSetup=0)
    sh = Shot.objects.get(IsComplete=0,Session_id=s.id)

    sh.HogPingTime2 = unparsed_value  # no need to do any parsing since this is the only value in this transmission.
    sh.HogDistance2 = DistanceCalc(sh.HogPingTime2,sh.TempC,sh.Humidity)
    sh.save()

    return  HttpResponse(unparsed_value)


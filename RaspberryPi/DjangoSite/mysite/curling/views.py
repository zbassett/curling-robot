from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import AssignPersonForm, AssignRFIDForm, ClubForm, AssignRockRFIDForm, AssignRockRFIDForm, PersonForm, AssignSheetForm

from .models import Club, Person, Session, SessionPerson, RFIDRawData, Shot, SessionRock, Sheet, Rock
from .functions import DistanceCalc
from .filters import SheetFilter
from django.views.generic.edit import CreateView
from channels import Group
from django.core import serializers
import simplejson as json


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
    return HttpResponseRedirect('/curling/setup/')

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
    return HttpResponseRedirect('/curling/setup/')

@login_required
def assignrocks(request):
    s = Session.objects.get_or_create(IsClosed=0)[0]
    
    if request.method == "POST":
        print(request.POST)
        rocks_on_sheet = Rock.objects.filter(Sheet=Sheet.objects.get(pk=request.POST['sheet_to_assign']))
        for r in rocks_on_sheet:
            sr = SessionRock.objects.create(Rock=r,Session=s)

    return HttpResponseRedirect('/curling/setup/')

@login_required
def assignrockrfid(request):
    s = Session.objects.get_or_create(IsClosed=0)[0]
    s.IsSetup = 1
    s.save()
    if request.method == "POST":
        form_RFID = AssignRockRFIDForm(request.POST)
        if form_RFID.is_valid():
            r = SessionRock.objects.get(pk=request.POST['rock_to_assign']) 
            r.RFID=RFIDRawData.objects.filter(id=request.POST['rfid_value']).values_list('RFIDValue',flat=True)[0]
            r.save()

            rf = RFIDRawData.objects.all()
            rf.delete()

        #form_class = AssignRockRFIDForm
    return HttpResponseRedirect('/curling/setup/')

@login_required
def setup(request):
    s = Session.objects.get_or_create(IsClosed=0)[0]
    s.IsSetup = 1
    s.save()

    form_class = AssignPersonForm
    form_RFID = AssignRFIDForm
    form_sheet = AssignSheetForm
    form_Rock_RFID = AssignRockRFIDForm

    template = "curling/setup.html"
    context = {'form': form_class, 'formRFID': form_RFID, 'form_sheet': form_sheet, 'form_Rock_RFID': form_Rock_RFID, 'Session': s}
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
    context = {'most_recent_shot': most_recent_shot, 'Session': s}
    return render( request, template, context )

@login_required
def endsession(request):
    print('EndSessionRequest')
    s = Session.objects.all()
    #print('ROCKsetup')
    s.update(IsClosed = 1)
    return HttpResponseRedirect('/curling/')

@login_required
def club(request):
    latest_club_list = Club.objects.order_by('Name')
    context = {'latest_club_list': latest_club_list}
    return render(request, 'curling/clublist.html', context)

@login_required
def addclub(request):
    if request.method == "POST":
        print request.POST
        form_class = ClubForm(request.POST)
        if form_class.is_valid():
            c = Club(Name=request.POST['Name'],Country=request.POST['Country'],Address1=request.POST['Address1'],Address2=request.POST['Address2'],City=request.POST['City'],State=request.POST['State'],Zip=request.POST['Zip'],NumberOfSheets=request.POST['NumberOfSheets'])
            c.save()

            #create sheet objects for the new club
            if c.NumberOfSheets > 0:
                for x in range(1, int(c.NumberOfSheets)+1):
                    s = Sheet.objects.create(Club=c,SheetLocalID=x)
                    #add rocks to sheet
                    for y in range (1, 8):
                        r = Rock.objects.create(Sheet=s,RockLocalID=y,Color='red')
                        r = Rock.objects.create(Sheet=s,RockLocalID=y,Color='yellow')

            latest_club_list = Club.objects.order_by('Name')
            context = {'latest_club_list': latest_club_list}
            return redirect('curling/club/')
    else:
        form_class = ClubForm()
        context = {'form': form_class}
        return render(request, 'curling/addclub.html', context)

@login_required
def editclub(request,club_id):
    print "edit club"
    if request.method == "POST":
        print request.POST
        form_class = ClubForm(request.POST)
        if form_class.is_valid():
            c = Club.objects.get(pk=club_id)
            c.Name=request.POST['Name']
            c.Country=request.POST['Country']
            c.Address1=request.POST['Address1']
            c.Address2=request.POST['Address2']
            c.City=request.POST['City']
            c.State=request.POST['State']
            c.Zip=request.POST['Zip']
            c.NumberOfSheets=request.POST['NumberOfSheets']
            c.save()

            #create sheet objects for the new club
            #if c.NumberOfSheets > 0:
                #for x in range(1, int(c.NumberOfSheets)+1):
                    #s = Sheet.objects.create(Club=c,SheetLocalID=x)
                    #add rocks to sheet
                    #for y in range (1, 8):
                        #r = Rock.objects.create(Sheet=s,RockLocalID=y,Color='red')
                        #r = Rock.objects.create(Sheet=s,RockLocalID=y,Color='yellow')

            latest_club_list = Club.objects.order_by('Name')
            context = {'latest_club_list': latest_club_list}
            return HttpResponseRedirect('/curling/club/')
    else:
        form_class = ClubForm()
        context = {'form': form_class}
        return render(request, 'curling/addclub.html', context)

@login_required
def clubdetail(request, club_id):
    model = get_object_or_404(Club.objects, pk = club_id)
    template_name = 'curling/clubdetail.html'
    form = ClubForm(instance=model)
    context = {'model': model,'form': form}
    return render( request, template_name, context )



@login_required
def person(request):
    person_list = Person.objects.order_by('FirstName')
    context = {'person_list': person_list}
    return render(request, 'curling/personlist.html', context)

@login_required
def persondetail(request, person_id):
    model = get_object_or_404(Person.objects, pk = person_id)
    template_name = 'curling/persondetail.html'
    form = PersonForm(instance=model)
    context = {'model': model,'form': form}
    return render( request, template_name, context )

@login_required
def addperson(request):
    if request.method == "POST":
        print request.POST
        form_class = PersonForm(request.POST)
        if form_class.is_valid():
            p = Person(FirstName=request.POST['FirstName'],LastName=request.POST['LastName'],Hand=request.POST['Hand'],Club=Club.objects.get(pk=request.POST['Club']),YearStarted=request.POST['YearStarted'],Gender=request.POST['Gender'])
            p.save()

            person_list = Person.objects.order_by('FirstName')
            context = {'person_list': person_list}
            return redirect('curling/person/')
    else:
        form_class = PersonForm()
        context = {'form': form_class}
        return render(request, 'curling/addperson.html', context)

@login_required
def editperson(request,person_id):
    if request.method == "POST":
        print request.POST
        form_class = PersonForm(request.POST)
        if form_class.is_valid():
            p = Person.objects.get(pk=person_id)
            p.FirstName=request.POST['FirstName']
            p.LastName=request.POST['LastName']
            p.Hand=request.POST['Hand']
            p.Club=Club.objects.get(pk=request.POST['Club'])
            p.YearStarted=request.POST['YearStarted']
            p.Gender=request.POST['Gender']

            p.save()

            person_list = Club.objects.order_by('Person')
            context = {'person_list': person_list}
            return redirect('curling/person/')
    else:
        form_class = PersonForm()
        context = {'form': form_class}
        return render(request, 'curling/addperson.html', context)


@login_required
def sheet(request):
    sheet_list = Sheet.objects.all()
    sheet_filter = SheetFilter(request.GET, queryset=sheet_list)
    return render(request, 'curling/sheetlist.html', {'filter': sheet_filter})

def rfid(request):
    unparsed_value = request.POST.get('payloadvalue')
    origin_node = unparsed_value[-1:]
    rfid_value = unparsed_value[4:-2]
    #print(rfid_value)
    r = RFIDRawData(RFIDValue=rfid_value,SourceNode=origin_node)
    r.save()


    try:
        s = Session.objects.get(IsClosed=0,IsSetup=1)
        groupname = 'setup%d' % s.id
        data = serializers.serialize('json',[r])
        print data
        Group(groupname).send({
            "text": data,
        })
    except Session.DoesNotExist:
        print("NoSetupSessions")
    

    try:
        s = Session.objects.get(IsClosed=0,IsSetup=0)
        
        try:
            p = SessionPerson.objects.get(Session=s.id,RFID=rfid_value)
            sh, created = Shot.objects.get_or_create(IsComplete=0,Session_id=s.id,HasReceivedData=0)
            sh.Person_id=p.Person_id
            sh.save()
            
            groupname = 'session%d' % s.id
            obj_pre = serializers.serialize("json", [sh])
            obj = json.loads(obj_pre)
            if sh.Person:
                obj[0]['fields']['PersonName'] = "%s %s" % (sh.Person.FirstName, sh.Person.LastName)
            else:
                obj[0]['fields']['PersonName'] = None

            if sh.Rock:
                obj[0]['fields']['ClubName'] = "%s" % (sh.Rock.Sheet.Club.Name)
                obj[0]['fields']['RockLabel'] = "%s %s" % (sh.Rock.Color, sh.Rock.RockLocalID)
                obj[0]['fields']['SheetLabel'] = "Sheet %s" % (sh.Rock.Sheet.SheetLocalID)
            else:
                obj[0]['fields']['ClubName'] = None
                obj[0]['fields']['RockLabel'] = None
                obj[0]['fields']['SheetLabel'] = None
            print obj
            Group(groupname).send({
                "text": json.dumps(obj),
            })

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

            groupname = 'session%d' % s.id
            obj_pre = serializers.serialize("json", [sh])
            obj = json.loads(obj_pre)
            if sh.Person:
                obj[0]['fields']['PersonName'] = "%s %s" % (sh.Person.FirstName, sh.Person.LastName)
            else:
                obj[0]['fields']['PersonName'] = None

            if sh.Rock:
                obj[0]['fields']['ClubName'] = "%s" % (sh.Rock.Sheet.Club.Name)
                obj[0]['fields']['RockLabel'] = "%s %s" % (sh.Rock.Color, sh.Rock.RockLocalID)
                obj[0]['fields']['SheetLabel'] = "Sheet %s" % (sh.Rock.Sheet.SheetLocalID)
            else:
                obj[0]['fields']['ClubName'] = None
                obj[0]['fields']['RockLabel'] = None
                obj[0]['fields']['SheetLabel'] = None
            print obj
            Group(groupname).send({
                "text": json.dumps(obj),
            })

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
        sheet_width = sh.Rock.Sheet.Width
    else:
    	rock_diameter = Rock._meta.get_field('Diameter').default #292.1  #using a default value of 11.5" (292.1mm)
        sheet_width = Sheet._meta.get_field('Width').default

    sh.HogSpeed = float(rock_diameter) / float(sh.HogTripDuration)
    sh.TeeSpeed = float(rock_diameter) / float(sh.TeeTripDuration)
    sh.AvgSplitSpeed = float(6.4008) / (float(sh.TeeHogSplit)/1000)  #tee-hog = 21 feet = 6.4008 meters
    sh.TeeDistance = DistanceCalc(sh.TeePingTime,sh.TempC,sh.Humidity) - (sheet_width/100) / 2 + (rock_diameter/100) / 2  #returns position left (negative) or right (positive) of center line
    sh.HogDistance1 = DistanceCalc(sh.HogPingTime1,sh.TempC,sh.Humidity) - (sheet_width/100) / 2 + (rock_diameter/100) / 2 


    sh.save()

    groupname = 'session%d' % s.id
    obj_pre = serializers.serialize("json", [sh])
    obj = json.loads(obj_pre)
    if sh.Person:
        obj[0]['fields']['PersonName'] = "%s %s" % (sh.Person.FirstName, sh.Person.LastName)
    else:
        obj[0]['fields']['PersonName'] = None
    if sh.Rock:
        obj[0]['fields']['ClubName'] = "%s" % (sh.Rock.Sheet.Club.Name)
        obj[0]['fields']['RockLabel'] = "%s %s" % (sh.Rock.Color, sh.Rock.RockLocalID)
        obj[0]['fields']['SheetLabel'] = "Sheet %s" % (sh.Rock.Sheet.SheetLocalID)
    else:
        obj[0]['fields']['ClubName'] = None
        obj[0]['fields']['RockLabel'] = None
        obj[0]['fields']['SheetLabel'] = None
    print obj
    Group(groupname).send({
        "text": json.dumps(obj),
    })

    return  HttpResponse(unparsed_value)

def shot2(request):
    unparsed_value = request.POST.get('payloadvalue')[6:]

    s = Session.objects.get(IsClosed=0,IsSetup=0)
    sh = Shot.objects.get(IsComplete=0,Session_id=s.id)

    if sh.Rock:
    	rock_diameter = sh.Rock.Diameter
        sheet_width = sh.Rock.Sheet.Width
    else:
    	rock_diameter = Rock._meta.get_field('Diameter').default #292.1  #using a default value of 11.5" (292.1mm)
        sheet_width = Sheet._meta.get_field('Width').default

    sh.HogPingTime2 = unparsed_value  # no need to do any parsing since this is the only value in this transmission.
    sh.HogDistance2 = DistanceCalc(sh.HogPingTime2,sh.TempC,sh.Humidity) - (sheet_width/100) / 2 + (rock_diameter/100) / 2 
    sh.save()

    return  HttpResponse(unparsed_value)


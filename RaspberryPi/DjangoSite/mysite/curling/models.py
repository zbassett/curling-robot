from __future__ import unicode_literals
from django.db import models
from django.utils import timezone

class Club(models.Model):
    Name = models.CharField(max_length=200)
    Country = models.CharField(max_length=200,null=True,blank=True)
    Address1 = models.CharField(max_length=200,null=True,blank=True)
    Address2 = models.CharField(max_length=200,null=True,blank=True)
    City = models.CharField(max_length=200,null=True,blank=True)
    State = models.CharField(max_length=200,null=True,blank=True)
    Zip = models.CharField(max_length=200,null=True,blank=True)
    NumberOfSheets = models.PositiveIntegerField(default=0)
    LastUpdated = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.Name

class Sheet(models.Model):
    Club = models.ForeignKey(Club, on_delete=models.CASCADE)
    SheetLocalID = models.CharField(max_length=200)
    Width = models.FloatField(default=426.72) #14feet = 426.72cm
    def __str__(self):
        return '{} - {}'.format(self.Club, self.SheetLocalID)

class Person(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    HAND_CHOICES = (
        ('L', 'Left'),
        ('R', 'Right'),
    )
    FirstName = models.CharField(max_length=200)
    LastName = models.CharField(max_length=200)
    Hand = models.CharField(max_length=1, choices=HAND_CHOICES)
    Club = models.ForeignKey(Club, on_delete=models.CASCADE)
    YearStarted = models.IntegerField(null=True)
    Gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    LastUpdated = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return '{} {}'.format(self.FirstName, self.LastName)

class Rock(models.Model):
    Sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE)
    RockLocalID = models.CharField(max_length=200)
    Color = models.CharField(max_length=200)
    Diameter = models.FloatField(default=292.1) #11.5 inches
    LastUpdated = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return '{} - {} {}'.format(self.Sheet, self.Color, self.RockLocalID)

class Session(models.Model):
    Initiated = models.DateTimeField(default=timezone.now)
    Club = models.ForeignKey(Club, on_delete=models.CASCADE, default=None, blank=True, null=True)
    IsClosed = models.BooleanField(default=0)
    IsSetup = models.BooleanField(default=0)
    def __str__(self):
        return self.Initiated

class Shot(models.Model):
    Rock = models.ForeignKey(Rock, on_delete=models.CASCADE, null=True)
    Person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)
    Session = models.ForeignKey(Session, on_delete=models.CASCADE)
    TeeTripMasterTime = models.DateTimeField(null=True)
    TeeHogSplit = models.IntegerField(null=True)
    TeeTripDuration = models.IntegerField(null=True)
    HogTripDuration = models.IntegerField(null=True)
    TeeSpeed = models.FloatField(null=True)
    HogSpeed = models.FloatField(null=True)
    AvgSplitSpeed = models.FloatField(null=True)
    TempC = models.FloatField(null=True)
    Humidity = models.FloatField(null=True)
    TeePingTime = models.IntegerField(null=True)
    TeeDistance = models.FloatField(null=True)
    HogPingTime1 = models.IntegerField(null=True)
    HogPingTime2 = models.IntegerField(null=True)
    HogDistance1 = models.FloatField(null=True)
    HogDistance2 = models.FloatField(null=True)
    BroomPingTime = models.IntegerField(null=True)
    BroomDistance = models.FloatField(null=True)
    BroomInputMethod = models.FloatField(max_length=200,null=True,blank=True)
    IsComplete = models.BooleanField(default=0)
    HasReceivedData = models.BooleanField(default=0)
    def FormattedTeeHogSplit(self):
        return '{0:.2f}'.format(float(self.TeeHogSplit)/1000)
    def __str__(self):
        return self.TeeTripMasterTime
	
class SessionPerson(models.Model):
    Session = models.ForeignKey(Session, on_delete=models.CASCADE)
    Person = models.ForeignKey(Person, on_delete=models.CASCADE)
    RFID = models.CharField(max_length=200,null=True,blank=True)
    def __str__(self):
        return self.Person
	
class SessionRock(models.Model):
    Session = models.ForeignKey(Session, on_delete=models.CASCADE)
    Rock = models.ForeignKey(Rock, on_delete=models.CASCADE)
    RFID = models.CharField(max_length=200,null=True,blank=True)
    def __str__(self):
        return self.Rock

class RFIDRawData(models.Model):
    RFIDValue = models.CharField(max_length=100)
    SourceNode = models.CharField(max_length=10)
    LastUpdated = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.RFIDValue
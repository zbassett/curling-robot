from django.forms import ModelChoiceField
from .models import Person, Session, SessionPerson, RFIDRawData

class AssignRFIDChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        rfid_value = 'no RFID assigned' if obj.RFID is None else obj.RFID
        return Person.objects.filter(id=obj.Person_id).values_list('FirstName',flat=True)[0] + '  --  ' + rfid_value

class AssignRockRFIDChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        rfid_value = 'no RFID assigned' if obj.RFID is None else obj.RFID
        return obj.Rock.Color  + '  --  ' + obj.Rock.RockLocalID  + '  --  ' + rfid_value



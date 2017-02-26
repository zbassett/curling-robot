from django import forms
from django.forms import ModelForm
from .models import Person, Session, SessionPerson, RFIDRawData, SessionRock, Rock, Club
from .fields import AssignRFIDChoiceField, AssignRockRFIDChoiceField

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML
from crispy_forms.bootstrap import FormActions

gender_choice = (('male','Male',),('female','Female',))
hand_choice =  (('left','Left',),('right','Right',))

class AssignPersonForm(forms.Form):
    #identify current session
    s = Session.objects.filter(IsClosed=0)
    #list of people in current session:
    inner_qs = SessionPerson.objects.filter(Session_id=s.values('id'))
    #list of everyone EXCEPT people in current session
    person_to_assign = forms.ModelChoiceField(Person.objects.exclude(id__in=inner_qs.values('Person_id')).order_by('FirstName'))
    def __init__(self, *args, **kwargs):
        super(AssignPersonForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-addPersonForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'add_person'

        self.helper.add_input(Submit('submit', 'Submit'))

class AssignRFIDForm(forms.Form):
    #identify current session
    s = Session.objects.filter(IsClosed=0)
    #list of people in current session:
    inner_qs = SessionPerson.objects.filter(Session_id=s.values('id'))
    #person_to_assign = forms.ModelChoiceField(Person.objects.filter(id__in=inner_qs.values('Person_id')).order_by('FirstName'))
    
    person_to_assign = AssignRFIDChoiceField(inner_qs)

    qs = RFIDRawData.objects.order_by('-id')
    rfid_value = forms.ModelChoiceField(qs, empty_label=None)
    def __init__(self, *args, **kwargs):
        super(AssignRFIDForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-addRFIDForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'assign_rfid'

        self.helper.add_input(Submit('submit', 'Submit'))

class AddPersonForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    gender = forms.ChoiceField(widget=forms.RadioSelect, choices=gender_choice)
    hand = forms.ChoiceField(widget=forms.RadioSelect, choices=hand_choice)

class AddClubForm(forms.ModelForm):
    #club_name = forms.CharField()
    #country_field = forms.CharField(required=False)
    #address1_field = forms.CharField(required=False)
    #address2_field = forms.CharField(required=False)
    #city_field = forms.CharField(required=False)
    #state_field = forms.CharField(required=False)
    #zip_field = forms.CharField(required=False)
    class Meta:
        model = Club
        fields = ['Name','Country','Address1','Address2','City','State','Zip','NumberOfSheets']

    def __init__(self, *args, **kwargs):
        super(AddClubForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-addAddClubForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'add_club/'

        self.helper.layout.append(
            FormActions(
                Submit('save', 'Save changes'),
                #Button('cancel', 'Cancel')
            )
        )


class AssignRockForm(forms.Form):
    #identify current session
    s = Session.objects.filter(IsClosed=0)
    #list of people in current session:
    inner_qs = SessionRock.objects.filter(Session_id=s.values('id'))
    #list of everyone EXCEPT people in current session
    rock_to_assign = forms.ModelChoiceField(Rock.objects.exclude(id__in=inner_qs.values('Rock_id')))

class AssignRockRFIDForm(forms.Form):
    #identify current session
    s = Session.objects.filter(IsClosed=0)
    #list of people in current session:
    inner_qs = SessionRock.objects.filter(Session_id=s.values('id'))
        
    rock_to_assign = AssignRockRFIDChoiceField(inner_qs)

    qs = RFIDRawData.objects.order_by('-id')
    rfid_value = forms.ModelChoiceField(qs, empty_label=None)
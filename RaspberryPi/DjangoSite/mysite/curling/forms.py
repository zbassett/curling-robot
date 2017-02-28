from django import forms
from django.forms import ModelForm
from .models import Person, Session, SessionPerson, RFIDRawData, SessionRock, Rock, Club, Sheet
from .fields import AssignRFIDChoiceField, AssignRockRFIDChoiceField
from .filters import RockFilter

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML, Field
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
        self.helper.form_action = 'assign_person/'

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
        self.helper.form_action = 'assign_rfid/'
        self.helper.layout = Layout(
            Field('person_to_assign'),
            Field('rfid_value', css_class='rfidfield')
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['FirstName','LastName','Hand','Club','YearStarted','Gender']

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-PersonForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'add_edit_person/'
        self.helper.layout.append(
            FormActions(
                Submit('save', 'Save changes'),
                #Button('cancel', 'Cancel')
            )
        )

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['Name','Country','Address1','Address2','City','State','Zip','NumberOfSheets']

    def __init__(self, *args, **kwargs):
        super(ClubForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-ClubForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'add_edit_club/'

        self.helper.layout.append(
            FormActions(
                Submit('save', 'Save changes'),
                #Button('cancel', 'Cancel')
            )
        )

class AssignSheetForm(forms.Form):
    sheet_to_assign = forms.ModelChoiceField(Sheet.objects.all())
    def __init__(self, *args, **kwargs):
        super(AssignSheetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-addSheetForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'assign_sht/'

        self.helper.add_input(Submit('submit', 'Submit'))

class AssignRockRFIDForm(forms.Form):
    #identify current session
    s = Session.objects.filter(IsClosed=0)
    #list of people in current session:
    inner_qs = SessionRock.objects.filter(Session_id=s.values('id')).order_by('Rock__Color','Rock__RockLocalID')
    
    rock_to_assign = AssignRockRFIDChoiceField(inner_qs)

    qs = RFIDRawData.objects.order_by('-id')
    rfid_value = forms.ModelChoiceField(qs, empty_label=None)
    def __init__(self, *args, **kwargs):
        super(AssignRockRFIDForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-addRockRFIDForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'assign_rock_rfid/'
        self.helper.layout = Layout(
            Field('rock_to_assign'),
            Field('rfid_value', css_class='rfidfield')
        )

        self.helper.add_input(Submit('submit', 'Submit'))

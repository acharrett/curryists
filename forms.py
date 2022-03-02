from django import forms
from .models import Attendance

class AttendForm(forms.ModelForm):
	name = forms.CharField(max_length=50)
	email = forms.EmailField(max_length=50)
	num_attendees = forms.IntegerField(min_value=1,max_value=10)

	class Meta:
		model = Attendance
		fields = ( 'name','email','num_attendees' )

class FindmeForm(forms.Form):
	email = forms.EmailField(max_length=50)


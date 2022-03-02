from django.db import models

# Create your models here.

class City(models.Model):
	name = models.CharField(max_length=50)
	email_list = models.CharField(max_length=200)
	def __str__(self):
		return self.name

class Location(models.Model):
	name = models.CharField(max_length=200)
	maplink = models.CharField(max_length=1000)
	menulink = models.CharField(max_length=1000)
	address = models.CharField(max_length=1000)
	postcode = models.CharField(max_length=10)
	city = models.ForeignKey(City)	
	def __str__(self):
		return self.name

class Event(models.Model):
	name = models.CharField(max_length=200)
	description = models.CharField(max_length=1000)
	time = models.DateTimeField()
	notified = models.BooleanField(default=0,editable=False)
	location = models.ForeignKey(Location)
	max_attendance = models.IntegerField(default=0)
	def __str__(self):
		return self.name

class Attendance(models.Model):
	name = models.CharField(max_length=50)
	email = models.CharField(max_length=50)
	num_attendees = models.IntegerField(default=1)
	event = models.ForeignKey(Event)
	def __str__(self):
		return self.name


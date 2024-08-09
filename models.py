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
	city = models.ForeignKey(City, on_delete=models.DO_NOTHING)
	def __str__(self):
		return self.name

class Event(models.Model):
	name = models.CharField(max_length=200)
	description = models.CharField(max_length=1000)
	time = models.DateTimeField()
	notified = models.BooleanField(default=0,editable=False)
	location = models.ForeignKey(Location, on_delete=models.DO_NOTHING)
	max_attendance = models.IntegerField(default=0)
	def __str__(self):
		return self.name

class Attendance(models.Model):
	name = models.CharField(max_length=50)
	email = models.CharField(max_length=50)
	num_attendees = models.IntegerField(default=1)
	cancelled = models.BooleanField(default=0)
	event = models.ForeignKey(Event, on_delete=models.DO_NOTHING)
	class Meta:
		unique_together = ["email", "event"]
	def __str__(self):
		return self.name


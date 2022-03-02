from django.contrib import admin
from booking.models import City,Location,Event

admin.site.register(City)
admin.site.register(Location)
admin.site.register(Event)

#class EventAdmin(admin.ModelAdmin):
#	list_display = ("name","description","time","locaion")

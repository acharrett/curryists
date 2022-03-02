""" Curryists booking views """
import datetime
import pytz
#from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.shortcuts import render, get_object_or_404
#from django.http import HttpResponseRedirect, HttpResponse
from django.http import HttpResponseRedirect
#from django.views.generic import ListView,DetailView
#from django.views.generic.edit import FormView
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
#from booking.models import City,Location,Event,Attendance
from booking.models import Event,Attendance
from booking.forms import AttendForm,FindmeForm
from booking.conf import CurryConfig

def event_list(request):
    """ list active events """
    hour_ago = datetime_now() - datetime.timedelta(hours = 1)
    list_of_events = Event.objects.filter(time__gte=hour_ago)

    return render(
                     request,
                     'event_list.html',
                     {
                       'object_list': list_of_events,
                       'request': request,
                     }
                 )

def historic_list(request):
    """ list past events """
    timenow = datetime_now()
    list_of_events = Event.objects.filter(time__lte=timenow).order_by('-time')
    return render(
                     request,
                     'historic_list.html',
                     {
                         'object_list': list_of_events,
                         'request': request,
                     }
                 )


def attend_new(request,eventid):
    """ handle a new attendance """
    this_event = get_object_or_404(Event, pk=eventid)

    if request.method == "POST":
        form = AttendForm(request.POST)

        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.event = this_event
            attendance.save()

            eventtime = EventTime(attendance.event.time,CurryConfig.timezone)


            message = render_to_string(
                                          'invite.email',
                                          {
                                              'event': this_event,
                                              'curryconfig': CurryConfig,
                                              'eventtime': eventtime,
                                          }
                                      )

            invite = generate_invite(
                                        attendance,
                                        this_event,
                                        message,
                                        eventtime,
                                    )

            email = EmailMultiAlternatives('Invitation: ' + this_event.name,
                message,
    			CurryConfig.email_from_name +' <' + CurryConfig.email_from_address + '>',
    			[ attendance.email ],
    			headers={ 'Sender': CurryConfig.email_from_address },
            )

            email.attach_alternative(invite,"text/calendar; method=REQUEST")

            email.send()

        to_return = HttpResponseRedirect(reverse('eventlist'))

    else:
        form = AttendForm(initial={'num_attendees':1})
        now_tz=datetime_now()

#        if this_event.time < now_tz:
#            past = True
#        else:
#            past = False

        past = bool(this_event.time < now_tz)

        attend_list = Attendance.objects.filter(event=eventid)
        total_attendance=0

        for attend in attend_list:
            total_attendance += attend.num_attendees

        to_return = render(
                         request,
                         'attend.html',
                         {
                             'form': form,
                             'event': this_event,
                             'request': request,
                             'past': past,
                             'total_attendance': total_attendance,
                         }
                     )

    return to_return


def findme(request):
    """ look up someone's existing registrations """
    if request.method == "POST":
        form = FindmeForm(request.POST)

        if form.is_valid():
            timenow = datetime_now()
            attend_list = Attendance.objects.filter(
                event__time__gte=timenow
            ).filter(
                email=request.POST['email']
            )
            to_return = render(
                             request,
                             'attendence_list.html',
                             {
                                 'attend_list': attend_list,
                                 'request': request,
                             }
                         )
        else:
            to_return = render(request, 'findme.html', {'form': form, 'request': request, })

    else:
        form = FindmeForm
        to_return = render(request, 'findme.html', {'form': form, 'request': request, })

    return to_return

def cancelme(request,attendid,email):
    """ cancel a registration """
    attend = get_object_or_404(Attendance, pk=attendid)

    if str.lower(str(attend.email)) == str.lower(str(email)):
        generate_cancellation(attend)
        attend.delete()
        message = "Registration cancelled"
    else:
        message = "Invalid parameters"

    return render(request,'message.html', { 'message': message, 'request': request, })

@login_required(login_url='/admin/login/')
def nuke(request,attendid):
    """ admin remove a registration """
    attend = get_object_or_404(Attendance, pk=attendid)
    event_id = attend.event.id
    attend.delete()
    return HttpResponseRedirect('/curry/event/%d'%event_id)

@login_required(login_url='/admin/login/')
def viewevent(request,eventid):
    """ view an event """
    event = get_object_or_404(Event,pk=eventid)
    attend_list = Attendance.objects.filter(event=eventid)
    total_attendance=0

    for attend in attend_list:
        total_attendance += attend.num_attendees

    return render(
                     request,
                     'event.html',
                     {
                         'event' : event,
                         'attend_list': attend_list,
                         'total_attendance': total_attendance,
                         'request': request,
                     }
                 )


@login_required(login_url='/admin/login/')
def viewhistoric(request,eventid):
    """ view a event that has passed """
    event = get_object_or_404(Event,pk=eventid)
    attend_list = Attendance.objects.filter(event=eventid)
    total_attendance=0

    for attend in attend_list:
        total_attendance += attend.num_attendees

    return render(
                     request,
                     'historic.html',
                     {
                         'event' : event,
                         'attend_list': attend_list,
                         'total_attendance': total_attendance,
                         'request': request,
                     }
                 )


@login_required(login_url='/admin/login/')
def notify(request,eventid):
    """ send the mailing list a notification of the event """
    event = get_object_or_404(Event,pk=eventid)

    now_tz=datetime_now()
    message = render_to_string(
                                  'notification.email',
                                  {
                                      'event': event,
                                      'curryconfig': CurryConfig,
                                  }
                              )
    if event.notified:
        subject="Reminder of Curry Event"
    else:
        subject="New Curry Event Notification"

    if event.time > now_tz:
        email = EmailMessage(subject,
                message,
    			CurryConfig.email_from_name +' <' + CurryConfig.email_from_address + '>',
                [ event.location.city.email_list ],
    			headers={ 'Sender': CurryConfig.email_from_address },
        )

        email.send()

        if event.notified is False:
            event.notified=True
            event.save()

    return HttpResponseRedirect(reverse('eventlist'))

def generate_invite(attendance,event,message,eventtime):
    """ create the invitation to send once someone has signed up """
    message_body = message.replace("\n", "\\n")

    eventtime = EventTime(event.time,CurryConfig.timezone)

    invite = render_to_string(
                                 'invite.ical',
                                 {
                                     'attendance': attendance,
                                     'event': event,
                                     'eventtime': eventtime,
                                     'message_body': message_body,
                                     'curryconfig': CurryConfig,
                                 }
                             )

    return invite

def datetime_now():
    """ generate a datetime of the current time """
    my_timezone=pytz.timezone(CurryConfig.timezone)
    now_tz=datetime.datetime.now(my_timezone)
    return now_tz

def generate_cancellation(attendance):
    """ generate an invite cancellation if someone has de-registered themselves """
    eventtime = EventTime(attendance.event.time,CurryConfig.timezone)

    cancel_ical = render_to_string(
                                      'cancel.ical',
                                      {
                                          'attendance': attendance,
                                          'curryconfig': CurryConfig,
                                          'reminder_hours': eventtime.reminder_hours,
                                          'eventtime_vcal': eventtime.start_vcal,
                                          'endtime_vcal': eventtime.end_vcal,
                                          'now_tz_stamp': eventtime.now_vcal,
                                      }
                                  )

    message = "You have cancelled your registration for this event"

    email = EmailMultiAlternatives('Cancelled: ' + attendance.event.name,
                 message,
                 CurryConfig.email_from_name +' <' + CurryConfig.email_from_address + '>',
                 [ attendance.email ],
                 headers={ 'Sender': CurryConfig.email_from_address },
             )

    email.attach_alternative(cancel_ical,"text/calendar; method=REQUEST")
    email.send()

class EventTime:
    """ a class for all the different ways we want to represent the start/end date of the event """

    def __init__(self,start_time,time_zone):

        my_tz = pytz.timezone(time_zone)
        time_now = datetime.datetime.now(my_tz)
        self.start_time_local = start_time.astimezone(pytz.timezone(time_zone))
        self.start_datetime = self.start_time_local
        self.start_string = self.start_time_local.strftime("%H:%M %a %d %b %Y")
        self.start_vcal = self.vcal_date(self.start_datetime)
        self.start_vcal = self.vcal_date(self.start_datetime)
        self.now_vcal = self.vcal_date(time_now)
        self.event_hour = self.start_datetime.strftime("%H")
        self.time_zone = time_zone
        self.event_length, self.reminder_hours = self.gen_event_length(self.event_hour)
        self.end_datetime = self.start_datetime + datetime.timedelta(hours=self.event_length)
        self.end_vcal = self.vcal_date(self.end_datetime)

    @staticmethod
    def vcal_date(my_datetime):
        """ parse the date in to vcal format for the invites """
        fmt = '%Y%m%dT%H%M%S'
        return my_datetime.strftime(fmt)

    @staticmethod
    def gen_event_length(event_hour):
        """ work out how long the event will be """
        # by default the event is 3 hours long
        event_length=3
        reminder_hours=2

        # unless it's before 2pm
        if int(event_hour) <= 14:
            event_length=1
            reminder_hours=1

        return [ event_length, reminder_hours ]

from django.conf.urls import url

from booking import views

urlpatterns = [
	url(r'^$', views.event_list, name='eventlist'),
	url(r'^attend/(\d+)', views.attend_new, name='attend_new'),
	url(r'^findme/', views.findme, name='findme'),
	url(r'^cancelme/(\d+)/(.+)/', views.cancelme, name='cancelme'),
	url(r'^nuke/(\d+)/', views.nuke, name='nuke'),
	url(r'^event/(\d+)', views.viewevent, name='viewevent'),
	url(r'^notify/(\d+)', views.notify, name='notify'),
	url(r'^viewhistoric/(\d+)', views.viewhistoric, name='viewhistoric'),
	url(r'^historic/', views.historic_list, name='historiclist'),
	url(r'^sendupdate/(\d+)', views.send_event_update, name='sendupdate'),
]


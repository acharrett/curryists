from django.conf import settings
from appconf import AppConf

class CurryConfig(AppConf):
    email_from_name = "Curry Bot"
    email_from_address = "currybot@example.com"
    calendar_id_domain = "example.com"
    attend_base_url = "https://example.com/curry/attend/"
    timezone = "Europe/London"



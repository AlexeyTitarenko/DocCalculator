from django.contrib import admin
from .models import Calculation
from .models import Subscriber

admin.site.register(Calculation)
admin.site.register(Subscriber)
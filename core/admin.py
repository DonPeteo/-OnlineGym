
from django.contrib import admin
from .models import Program, Video, PurchasedProgram

admin.site.register(Program)
admin.site.register(Video)
admin.site.register(PurchasedProgram)
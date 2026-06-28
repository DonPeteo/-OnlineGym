
from django.contrib import admin
from .models import Program, Video, PurchasedProgram, Review, Favorite

admin.site.register(Program)
admin.site.register(Video)
admin.site.register(PurchasedProgram)
admin.site.register(Review)
admin.site.register(Favorite)
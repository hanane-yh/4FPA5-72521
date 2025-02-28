from django.contrib import admin
from .models import Automobile, Part, PartFile

admin.site.register(Automobile)
admin.site.register(Part)
admin.site.register(PartFile)

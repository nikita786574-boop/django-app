from django.contrib import admin
from .models import SubSystem , Parameters, ParameterRelations
# Register your models here.
admin.site.register(SubSystem)
admin.site.register(Parameters)
admin.site.register(ParameterRelations)
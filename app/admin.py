from django.contrib import admin
from .models import SubSystem , Parameters, ParameterRelations
# Register your models here.

class SubSystemAdmin(admin.ModelAdmin):
    """Настройка отображения SubSystem в админке"""
    list_display = ('name', 'parent', 'is_root', 'number')
    list_filter = ('is_root',) # фальтр справа
    search_fields = ('name', 'description') # поле поиска
    ordering = ('number', )


admin.site.register(SubSystem, SubSystemAdmin)
admin.site.register(Parameters)
admin.site.register(ParameterRelations)

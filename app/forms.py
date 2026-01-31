from django import forms
from .models import SubSystem, Parameters, ParameterRelations
class SubSystemForm(forms.ModelForm):
    class Meta:
        model = SubSystem
        fields = ['name', 'description', 'parent','number','is_root']


class ParametersForm(forms.ModelForm):
    class Meta:
        model = Parameters
        fields = ['name', 'description', 'subsystem', 'number', 'measure']

class ParameterRelationsForm(forms.ModelForm):
    class Meta:
        model = ParameterRelations
        fields = ['is_affect']
        #fields = ['from_parameter', 'to_parameter','is_affect']
        widgets = {
            'is_affect': forms.CheckboxInput()
        }

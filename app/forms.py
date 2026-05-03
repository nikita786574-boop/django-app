from django import forms
from .models import SubSystem, Parameters, ParameterRelations, ParameterImportance
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

class ParameterRelationsFormSecond(forms.ModelForm):
    is_affect = forms.ChoiceField(
        choices = [
            (True, 'Да, влияет'),
            (False, 'Нет, не влияет')
        ],
        widget = forms.RadioSelect
    )
    class Meta:
        model = ParameterRelations
        fields=['is_affect']

class ParameterImportanceForm(forms.ModelForm):
    class Meta:
        model = ParameterImportance
        fields = ['value']
        widgets = {
            'value': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Введите важность'})
        }
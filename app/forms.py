from django import forms
from .models import SubSystem, Parameters, ParameterRelations, ParameterImportance


def _lock_number(form):
    """Поле number отображается, но не редактируется — назначается автоматически."""
    field = form.fields['number']
    field.required = False
    field.disabled = True
    field.help_text = 'Назначается автоматически (порядковый номер в рамках уровня)'


class SubSystemForm(forms.ModelForm):
    class Meta:
        model = SubSystem
        fields = ['name', 'description', 'parent','number','is_root']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _lock_number(self)


class ParametersForm(forms.ModelForm):
    class Meta:
        model = Parameters
        fields = ['name', 'description', 'subsystem', 'number', 'measure']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _lock_number(self)


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
            'value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите важность'})
               }


class ParameterRelationTypeForm(forms.ModelForm):
    relation_type = forms.ChoiceField(
        choices=ParameterImportance.RELATION_TYPE_CHOICES,
        widget=forms.RadioSelect,
        label='Тип связи',
    )

    class Meta:
        model = ParameterImportance
        fields = ['relation_type']

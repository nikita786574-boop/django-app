from django.db import models
from django.core.exceptions import ValidationError

class SubSystem(models.Model):
    name = models.CharField(max_length=200, help_text="Название подсистемы")
    description = models.TextField(blank = True, null=True, help_text="Описание назначения подсистемы")
    parent = models.ForeignKey('self',
                              on_delete = models.PROTECT,
                              blank = True,
                              null=True,
                              related_name = 'children',
                              help_text="Родительская подсистема (если есть)"
                              )
    is_root = models.BooleanField(blank=False, default = True, help_text="Является ли корневой подсистемой")
    number = models.IntegerField(help_text="Порядковый номер подсистемы")
    def __str__(self):
        return self.name
    def clean(self):
        if not (self.is_root is None) and not(self.parent is None):
            raise ValidationError({"is_root": "Корневая подсистема не может иметь родителя"})
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'parameters': [p.to_dict() for p in self.parameters.all()],
            'children': [child.to_dict() for child in self.children.all()],
            
        }


class Parameters(models.Model):
    name = models.CharField(max_length = 20, help_text="Название параметра")
    description = models.TextField(blank = True, null=True, help_text="Описание параметра")
    subsystem = models.ForeignKey(SubSystem,
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True,
                                  related_name='parameters',
                                  help_text="Подсистема, к которой относится параметр")
    number = models.IntegerField(help_text="Порядковый номер параметра")
    
    
    measure = models.CharField(max_length=15, help_text="Единица измерения")

    is_goal = models.BooleanField(default=False)
    influence_on_other = models.ManyToManyField('self',
                                        through = 'ParameterRelations',
                                        symmetrical=False,
                                        related_name='influence_on_me')
    def __str__(self):
        return f"Параметер: {self.name}; Подсистема: {self.subsystem}; Номер: {self.number};"
    def to_dict(self):
        return {
            'id':self.id,
            'name':self.name,
            'description': self.description or '',
            'measure': self.measure,
            'number': self.number,
            'is_goal': self.is_goal,
            'is_affect': False,
        }
    class Meta:
        unique_together=('subsystem', 'number')
    
class ParameterRelations(models.Model):
    from_parameter =  models.ForeignKey(Parameters,
                                        on_delete = models.CASCADE,
                                        related_name = 'outcoming_links')
    to_parameter = models.ForeignKey(Parameters,
                                     on_delete = models.CASCADE,
                                     related_name = 'incoming_links')
    is_affect = models.BooleanField(blank = True, null=True)

    def __str__(self):
        return f"{self.from_parameter} -> {self.to_parameter}"
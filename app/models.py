from django.db import models

class SubSystem(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank = True, null=True)
    parent = models.ForeignKey('self',
                              on_delete = models.PROTECT,
                              blank = True,
                              null=True,
                              related_name = 'children'
                              )
    is_root = models.BooleanField(blank=False, default = True)
    number = models.IntegerField()
    def __str__(self):
        return self.name
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'parameters': [p.to_dict() for p in self.parameters.all()],
            'children': [child.to_dict() for child in self.children.all()],
            
        }


class Parameters(models.Model):
    name = models.CharField(max_length = 20)
    description = models.TextField(blank = True, null=True)
    subsystem = models.ForeignKey(SubSystem,
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True,
                                  related_name='parameters')
    number = models.IntegerField()


    measure = models.CharField(max_length=15)

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
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse

from .utils import slugify_ru, unique_slug

class SubSystem(models.Model):
    name = models.CharField(max_length=200, help_text="Название подсистемы")
    slug = models.SlugField(max_length=255, unique=True, blank=True,
                            help_text="Идентификатор для URL (генерируется автоматически)")
    description = models.TextField(blank = True, null=True, help_text="Описание назначения подсистемы")
    parent = models.ForeignKey('self',
                              on_delete = models.PROTECT,
                              blank = True,
                              null=True,
                              related_name = 'children',
                              help_text="Родительская подсистема (если есть)"
                              )
    is_root = models.BooleanField(blank=False, default = True, help_text="Является ли корневой подсистемой")
    number = models.IntegerField(blank=True, help_text="Порядковый номер подсистемы (назначается автоматически)")
    def __str__(self):
        return self.name
    def clean(self):
        if self.is_root is True and self.parent is not None:
            raise ValidationError({"is_root": "Корневая подсистема не может иметь родителя"})
    def save(self, *args, **kwargs):
        if not self.number:
            siblings = SubSystem.objects.filter(parent=self.parent)
            if self.pk:
                siblings = siblings.exclude(pk=self.pk)
            self.number = (siblings.aggregate(m=models.Max('number'))['m'] or 0) + 1
        if not self.slug:
            self.slug = unique_slug(SubSystem, slugify_ru(self.name), exclude_pk=self.pk)
        super().save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse('show_d3_tree', kwargs={'system_slug': self.slug})
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description or '',
            'parameters': [p.to_dict() for p in self.parameters.all()],
            'children': [child.to_dict() for child in self.children.all()],

        }


class Parameters(models.Model):
    name = models.CharField(max_length = 50, help_text="Название параметра")
    slug = models.SlugField(max_length=320, unique=True, blank=True,
                            help_text="Зависимый идентификатор для URL (slug подсистемы + номер + название)")
    description = models.TextField(blank = True, null=True, help_text="Описание параметра")
    subsystem = models.ForeignKey(SubSystem,
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True,
                                  related_name='parameters',
                                  help_text="Подсистема, к которой относится параметр")
    number = models.IntegerField(blank=True, help_text="Порядковый номер параметра (назначается автоматически)")


    measure = models.CharField(max_length=15, help_text="Единица измерения")

    is_goal = models.BooleanField(default=False)
    influence_on_other = models.ManyToManyField('self',
                                        through = 'ParameterRelations',
                                        symmetrical=False,
                                        related_name='influence_on_me')
    def __str__(self):
        return f"Параметер: {self.name}; Подсистема: {self.subsystem}; Номер: {self.number};"
    def build_slug_base(self):
        """Зависимый slug: <slug подсистемы>--<номер>-<транслит названия>."""
        prefix = ''
        if self.subsystem_id and self.subsystem.slug:
            prefix = f"{self.subsystem.slug}--"
        return f"{prefix}{self.number}-{slugify_ru(self.name)}"
    def save(self, *args, **kwargs):
        if not self.number:
            siblings = Parameters.objects.filter(subsystem=self.subsystem)
            if self.pk:
                siblings = siblings.exclude(pk=self.pk)
            self.number = (siblings.aggregate(m=models.Max('number'))['m'] or 0) + 1
        if not self.slug:
            self.slug = unique_slug(Parameters, self.build_slug_base(), exclude_pk=self.pk)
        super().save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse('edit_parameter', kwargs={'parameter_slug': self.slug})
    def to_dict(self):
        return {
            'id':self.id,
            'name':self.name,
            'slug': self.slug,
            'description': self.description or '',
            'measure': self.measure,
            'number': self.number,
            'is_goal': self.is_goal,
            'is_affect': False,
        }
    class Meta:
        unique_together=('subsystem', 'number', 'name')

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

class ParameterImportance(models.Model):
    """В модель заностятся два параметра. Если value = -1, то второй важнее первого
    Если value = 1, то первый важнее второго"""

    RELATION_TYPE_CHOICES = [
        ('A1', 'А1 — Противоречивая'),
        ('A2', 'А2 — Согласованная'),
        ('A3', 'А3 — Нейтральная'),
    ]

    first_parameter = models.ForeignKey(Parameters,
                                        on_delete=models.CASCADE,
                                        related_name='first_parameter')
    second_parameter = models.ForeignKey(Parameters,
                                                                    on_delete=models.CASCADE,
                                         related_name='second_parameter')
    value = models.IntegerField(help_text='Кто влияет', default=0)
    relation_type = models.CharField(
        max_length=2,
        choices=RELATION_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text='Тип связи между параметрами (А1/А2/А3)',
    )

    def __str__(self):
        return f"{self.first_parameter.name} <-> {self.second_parameter.name} (value={self.value}, type={self.relation_type or '-'})"

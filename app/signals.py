from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ParameterRelations 

@receiver(post_save, sender=ParameterRelations)
@receiver(post_delete, sender=ParameterRelations)
def update_is_goal(sender, instance, **kwargs):
    """
    Обновляет поле is_goal у целевого параметра при создании или удалении связей
    """

    target_param = instance.to_parameter
    # смотрим, есть ли связь у этого параметра

    has_incoming_links = ParameterRelations.objects.filter(to_parameter=target_param).exists()
    
    if target_param.is_goal  != has_incoming_links:
        target_param.is_goal = has_incoming_links
        target_param.save(update_fields=['is_goal'])
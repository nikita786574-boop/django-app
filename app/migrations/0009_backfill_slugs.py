from django.db import migrations

from app.utils import slugify_ru


def _gen_unique(used, base, fallback):
    base = base or fallback
    slug = base
    counter = 2
    while slug in used:
        slug = f"{base}-{counter}"
        counter += 1
    used.add(slug)
    return slug


def forwards(apps, schema_editor):
    """Заполняем slug сверху вниз: сначала подсистемы, затем параметры."""
    SubSystem = apps.get_model('app', 'SubSystem')
    Parameters = apps.get_model('app', 'Parameters')

    sub_slugs = set()
    for sub in SubSystem.objects.all().order_by('pk'):
        sub.slug = _gen_unique(sub_slugs, slugify_ru(sub.name), 'subsystem')
        sub.save(update_fields=['slug'])

    par_slugs = set()
    for par in Parameters.objects.select_related('subsystem').all().order_by('pk'):
        prefix = ''
        if par.subsystem_id and par.subsystem.slug:
            prefix = f"{par.subsystem.slug}--"
        base = f"{prefix}{par.number}-{slugify_ru(par.name)}"
        par.slug = _gen_unique(par_slugs, base, f"parameter-{par.pk}")
        par.save(update_fields=['slug'])


def backwards(apps, schema_editor):
    SubSystem = apps.get_model('app', 'SubSystem')
    Parameters = apps.get_model('app', 'Parameters')
    SubSystem.objects.update(slug=None)
    Parameters.objects.update(slug=None)


class Migration(migrations.Migration):
    """Шаг 2/3: генерируем уникальные slug для существующих записей."""

    dependencies = [
        ('app', '0008_add_slug_nullable'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]

from django.db import migrations

GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']


def seed(apps, schema_editor):
    Stock = apps.get_model('blood', 'Stock')
    for g in GROUPS:
        Stock.objects.get_or_create(bloodgroup=g, defaults={'unit': 0})


class Migration(migrations.Migration):
    dependencies = [('blood', '0005_camps_notifications_priority')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]

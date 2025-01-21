# Generated by Django 5.1.5 on 2025-01-21 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_department_project_deposit_deposit_for'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deposit',
            name='deposit_for',
        ),
        migrations.AddField(
            model_name='deposit',
            name='deposit_type',
            field=models.CharField(choices=[('tithe', 'Tithe'), ('thanksgiving', 'Thanksgiving'), ('wedding', 'Wedding'), ('offertory', 'Offertory'), ('first_fruits', 'First Fruit'), ('church_projects', 'Church Project'), ('others', 'Others')], default='tithe', max_length=20),
        ),
    ]

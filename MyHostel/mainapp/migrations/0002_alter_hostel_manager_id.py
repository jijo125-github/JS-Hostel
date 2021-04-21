# Generated by Django 3.2 on 2021-04-21 08:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hostel',
            name='manager_id',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(99999)]),
        ),
    ]

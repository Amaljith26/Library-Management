# Generated by Django 5.2.3 on 2025-07-01 10:08

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0005_member_plan_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]

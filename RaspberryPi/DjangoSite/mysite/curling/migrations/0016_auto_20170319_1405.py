# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-19 14:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curling', '0015_auto_20170226_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shot',
            name='BroomDistance',
            field=models.FloatField(default=0),
        ),
    ]

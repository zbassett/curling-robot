# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-12 17:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('curling', '0010_auto_20170212_0059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='LastUpdated',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='person',
            name='FirstName',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='person',
            name='LastName',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='person',
            name='LastUpdated',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='rfidrawdata',
            name='LastUpdated',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='rock',
            name='LastUpdated',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='session',
            name='Initiated',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='sheet',
            name='SheetLocalID',
            field=models.CharField(default=14, max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sheet',
            name='Width',
            field=models.FloatField(default=14),
        ),
    ]

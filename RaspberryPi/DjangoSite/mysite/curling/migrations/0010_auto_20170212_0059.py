# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-12 00:59
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('curling', '0009_auto_20170211_1946'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shot',
            name='HogTripMasterTime',
        ),
        migrations.AddField(
            model_name='shot',
            name='TeeHogSplit',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='club',
            name='LastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 12, 0, 59, 43, 408427, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='person',
            name='LastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 12, 0, 59, 43, 415647, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='rfidrawdata',
            name='LastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 12, 0, 59, 43, 440186, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='rock',
            name='LastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 12, 0, 59, 43, 419845, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='session',
            name='Initiated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 12, 0, 59, 43, 422951, tzinfo=utc)),
        ),
    ]
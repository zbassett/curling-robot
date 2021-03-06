# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-11 19:46
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('curling', '0008_auto_20170211_1928'),
    ]

    operations = [
        migrations.AddField(
            model_name='shot',
            name='HasReceivedData',
            field=models.BooleanField(default=0),
        ),
        migrations.AlterField(
            model_name='club',
            name='LastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 11, 19, 46, 48, 683524, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='person',
            name='LastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 11, 19, 46, 48, 691343, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='rfidrawdata',
            name='LastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 11, 19, 46, 48, 715600, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='rock',
            name='LastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 11, 19, 46, 48, 695122, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='session',
            name='Initiated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 11, 19, 46, 48, 698311, tzinfo=utc)),
        ),
    ]

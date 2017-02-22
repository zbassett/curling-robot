# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-09 01:58
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('curling', '0006_auto_20170207_2336'),
    ]

    operations = [
        migrations.AddField(
            model_name='rfidrawdata',
            name='SourceNode',
            field=models.CharField(default=1, max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='club',
            name='LastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 9, 1, 58, 31, 157104, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='person',
            name='LastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 9, 1, 58, 31, 164136, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='rfidrawdata',
            name='LastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 9, 1, 58, 31, 187983, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='rock',
            name='LastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 9, 1, 58, 31, 168402, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='session',
            name='Initiated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 9, 1, 58, 31, 171450, tzinfo=utc)),
        ),
    ]

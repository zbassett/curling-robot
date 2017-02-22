# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-05 22:06
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('curling', '0004_auto_20170205_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='LastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 5, 22, 6, 27, 793840, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='person',
            name='LastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 5, 22, 6, 27, 801044, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='rfidrawdata',
            name='LastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 5, 22, 6, 27, 823649, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='rfidrawdata',
            name='RFIDValue',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='rock',
            name='LastUpdated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 5, 22, 6, 27, 804619, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='session',
            name='Initiated',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 5, 22, 6, 27, 807564, tzinfo=utc)),
        ),
    ]
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StudentApp', '0006_auto_20170213_2252'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='request',
            name='student_object',
        ),
        migrations.RemoveField(
            model_name='request',
            name='teacher',
        ),
        migrations.RemoveField(
            model_name='spendrequest',
            name='student',
        ),
        migrations.RemoveField(
            model_name='spendrequest',
            name='teacher',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='inbox_backup',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='spendbox_backup',
        ),
        migrations.AddField(
            model_name='classroom',
            name='GDs',
            field=models.ManyToManyField(to='StudentApp.GoodDeed'),
        ),
        migrations.AddField(
            model_name='classroom',
            name='PRs',
            field=models.ManyToManyField(to='StudentApp.Request'),
        ),
        migrations.AddField(
            model_name='classroom',
            name='Rewards',
            field=models.ManyToManyField(to='StudentApp.Reward'),
        ),
        migrations.AddField(
            model_name='classroom',
            name='SRs',
            field=models.ManyToManyField(to='StudentApp.SpendRequest'),
        ),
        migrations.AddField(
            model_name='request',
            name='teacher_name',
            field=models.CharField(default=b'', max_length=500),
        ),
        migrations.AddField(
            model_name='request',
            name='time_string',
            field=models.CharField(default=b'', max_length=1000),
        ),
        migrations.AddField(
            model_name='spendrequest',
            name='student_name',
            field=models.CharField(default=b'', max_length=500),
        ),
        migrations.AddField(
            model_name='spendrequest',
            name='teacher_name',
            field=models.CharField(default=b'', max_length=500),
        ),
        migrations.AddField(
            model_name='student',
            name='captain',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='student',
            name='spendrequests',
            field=models.ManyToManyField(to='StudentApp.SpendRequest'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='Requests',
            field=models.ManyToManyField(to='StudentApp.Request'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='Spendbox',
            field=models.ManyToManyField(to='StudentApp.SpendRequest'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StudentApp', '0009_teacher_curr_team'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='request',
            name='g_deed',
        ),
        migrations.RemoveField(
            model_name='reward',
            name='id_num',
        ),
        migrations.AddField(
            model_name='request',
            name='deed_name',
            field=models.CharField(default=b'', max_length=300),
        ),
        migrations.AddField(
            model_name='spendrequest',
            name='student_username',
            field=models.CharField(default=b'', max_length=500),
        ),
        migrations.AddField(
            model_name='team',
            name='PRs',
            field=models.ManyToManyField(to='StudentApp.Request'),
        ),
        migrations.AddField(
            model_name='team',
            name='SRs',
            field=models.ManyToManyField(to='StudentApp.SpendRequest'),
        ),
        migrations.AddField(
            model_name='team',
            name='dollars',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='team',
            name='rewards',
            field=models.ManyToManyField(to='StudentApp.Reward'),
        ),
    ]

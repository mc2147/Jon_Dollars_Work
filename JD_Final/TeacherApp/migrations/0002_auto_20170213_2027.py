# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('TeacherApp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gooddeed',
            name='teacher',
        ),
        migrations.RemoveField(
            model_name='reward',
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
        migrations.DeleteModel(
            name='GoodDeed',
        ),
        migrations.DeleteModel(
            name='Reward',
        ),
        migrations.DeleteModel(
            name='SpendRequest',
        ),
    ]

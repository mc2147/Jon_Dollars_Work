# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StudentApp', '0005_teacher_curr_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='teams',
            field=models.ManyToManyField(to='StudentApp.Team'),
        ),
        migrations.AlterField(
            model_name='team',
            name='teacher',
            field=models.CharField(default=b'', max_length=200),
        ),
    ]

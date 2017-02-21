# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StudentApp', '0008_team_captain_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='curr_team',
            field=models.CharField(default=b'', max_length=500),
        ),
    ]

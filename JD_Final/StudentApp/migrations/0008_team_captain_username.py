# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StudentApp', '0007_auto_20170214_1513'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='captain_username',
            field=models.CharField(default=b'', max_length=200),
        ),
    ]

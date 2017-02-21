# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StudentApp', '0010_auto_20170217_2358'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='dollars',
            field=models.IntegerField(default=0),
        ),
    ]

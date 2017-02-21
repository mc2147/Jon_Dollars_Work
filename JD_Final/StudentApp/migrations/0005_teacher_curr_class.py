# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StudentApp', '0004_auto_20170213_2113'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='curr_class',
            field=models.CharField(default=b'', max_length=500),
        ),
    ]

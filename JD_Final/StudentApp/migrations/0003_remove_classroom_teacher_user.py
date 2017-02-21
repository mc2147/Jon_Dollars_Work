# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StudentApp', '0002_auto_20170213_2027'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classroom',
            name='teacher_user',
        ),
    ]

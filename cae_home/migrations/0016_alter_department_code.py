# Generated by Django 4.0.5 on 2022-08-20 05:02

import cae_home.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cae_home', '0015_alter_department_options_alter_semester_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='code',
            field=cae_home.models.fields.CodeField(max_length=255, unique=True),
        ),
    ]
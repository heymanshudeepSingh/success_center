# Generated by Django 3.0.5 on 2020-04-03 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cae_home', '0003_auto_20200403_0246'),
    ]

    operations = [
        migrations.RenameField(
            model_name='major',
            old_name='active',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='wmuuser',
            old_name='active',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='wmuusermajorrelationship',
            old_name='active',
            new_name='is_active',
        ),
        migrations.AddField(
            model_name='userintermediary',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]

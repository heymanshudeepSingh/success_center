# Generated by Django 3.0.5 on 2020-04-03 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cae_home', '0002_room_is_row'),
    ]

    operations = [
        migrations.AddField(
            model_name='userintermediary',
            name='first_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='userintermediary',
            name='last_name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]

# Generated by Django 3.0.5 on 2020-11-24 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cae_home', '0006_software_softwaredetail'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(max_length=255, unique=True)),
                ('asset_tag', models.CharField(max_length=255, unique=True)),
                ('brand_name', models.CharField(max_length=255)),
                ('mac_address', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('ip_address', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('device_name', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Assets',
                'ordering': ('asset_tag',),
            },
        ),
    ]

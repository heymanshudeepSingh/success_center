# Generated by Django 4.0.5 on 2022-09-06 10:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cae_home', '0016_alter_department_code'),
        ('success_center_core', '0002_tutorlocations_studentusagelog_approved_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SuccessCtrProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('default_tutor_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='success_center_core.tutorlocations')),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='cae_home.profile')),
            ],
            options={
                'verbose_name': 'SuccessCenter User Profile',
                'verbose_name_plural': 'SuccessCenter User Profiles',
            },
        ),
    ]

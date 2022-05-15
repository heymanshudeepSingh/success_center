# Generated by Django 4.0.4 on 2022-05-15 10:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cae_home', '0012_rename_semesterdate_semester'),
    ]

    operations = [
        migrations.CreateModel(
            name='WmuClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255, unique=True)),
                ('description', models.CharField(max_length=255)),
                ('slug', models.SlugField(help_text='Used for urls referencing this Class.', max_length=255, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cae_home.department')),
            ],
            options={
                'verbose_name': 'Class',
                'verbose_name_plural': 'Classes',
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='StudentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bachelors_institution', models.CharField(blank=True, max_length=255, null=True)),
                ('bachelors_gpa', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('masters_institution', models.CharField(blank=True, max_length=255, null=True)),
                ('masters_gpa', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('wmu_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cae_home.wmuuser')),
            ],
            options={
                'verbose_name': 'Class',
                'verbose_name_plural': 'Classes',
                'ordering': ('pk',),
            },
        ),
    ]

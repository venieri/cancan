# Generated by Django 3.0.1 on 2020-01-02 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='score',
            field=models.FloatField(default=0),
        ),
    ]
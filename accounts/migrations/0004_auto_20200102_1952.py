# Generated by Django 3.0.1 on 2020-01-02 19:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20200102_1847'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='addreed_to_rules',
            new_name='agreed_to_rules',
        ),
    ]

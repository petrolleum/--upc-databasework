# Generated by Django 3.2.4 on 2023-06-11 05:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gascom', '0009_customer_money'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliery_staff',
            name='password',
        ),
        migrations.RemoveField(
            model_name='supplier',
            name='password',
        ),
    ]
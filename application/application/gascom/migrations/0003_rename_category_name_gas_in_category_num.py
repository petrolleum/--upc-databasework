# Generated by Django 3.2.4 on 2023-05-24 03:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gascom', '0002_customer_deliery_staff_gas_category_gas_in_gas_out_supplier'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gas_in',
            old_name='category_name',
            new_name='category_num',
        ),
    ]

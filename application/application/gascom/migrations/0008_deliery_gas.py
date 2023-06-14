# Generated by Django 3.2.4 on 2023-05-30 11:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gascom', '0007_gas_out_is_deliery'),
    ]

    operations = [
        migrations.CreateModel(
            name='deliery_gas',
            fields=[
                ('num', models.IntegerField(primary_key=True, serialize=False)),
                ('deliery_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='gascom.deliery_staff')),
                ('gas_out_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='gascom.gas_out')),
            ],
        ),
    ]
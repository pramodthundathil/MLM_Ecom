# Generated by Django 5.0.6 on 2024-08-13 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0007_business_volume_purchase_bv_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountdetails',
            name='ifsc_code',
            field=models.CharField(max_length=20),
        ),
    ]

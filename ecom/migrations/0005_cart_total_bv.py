# Generated by Django 5.0.6 on 2024-08-08 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecom', '0004_cart'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='total_bv',
            field=models.FloatField(default=0),
        ),
    ]

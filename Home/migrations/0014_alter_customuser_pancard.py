# Generated by Django 5.0.6 on 2024-10-09 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0013_alter_customuser_date_of_birth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='pancard',
            field=models.CharField(max_length=20, verbose_name='PAN card'),
        ),
    ]

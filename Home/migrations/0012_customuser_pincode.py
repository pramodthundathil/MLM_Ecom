# Generated by Django 5.0.6 on 2024-09-17 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0011_alter_accountdetails_branch_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='pincode',
            field=models.BigIntegerField(default=1),
        ),
    ]

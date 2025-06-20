# Generated by Django 5.2 on 2025-06-05 00:22

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app1', '0019_alter_product_id_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customuser',
            name='deleted_at',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='updated_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]

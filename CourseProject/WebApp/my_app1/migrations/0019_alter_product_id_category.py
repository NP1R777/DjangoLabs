# Generated by Django 5.2 on 2025-06-03 18:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app1', '0018_alter_application_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='id_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='my_app1.category'),
        ),
    ]

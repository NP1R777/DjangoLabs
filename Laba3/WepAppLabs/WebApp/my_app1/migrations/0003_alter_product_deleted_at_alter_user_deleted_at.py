# Generated by Django 5.1.6 on 2025-02-28 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app1', '0002_alter_product_deleted_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='deleted_at',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='deleted_at',
            field=models.DateField(blank=True, null=True),
        ),
    ]

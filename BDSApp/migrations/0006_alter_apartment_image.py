# Generated by Django 5.1.4 on 2025-02-15 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BDSApp', '0005_building_customer_rename_room_count_apartment_floor_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartment',
            name='image',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

# Generated by Django 4.0.6 on 2022-07-29 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0002_alter_data_filename_alter_data_timeframe'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='convertedfile',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
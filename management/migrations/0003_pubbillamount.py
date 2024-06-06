# Generated by Django 5.0.4 on 2024-05-22 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0002_expensepaidamount'),
    ]

    operations = [
        migrations.CreateModel(
            name='PUBBillAmount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pre_date', models.DateField(null=True)),
                ('prev_read', models.FloatField(default=0)),
                ('cur_date', models.DateField(null=True)),
                ('cur_read', models.FloatField(default=0)),
                ('total_units', models.FloatField(default=0)),
                ('refuse_amt', models.FloatField(default=0)),
                ('water_amt', models.FloatField(default=0)),
                ('gst', models.FloatField(default=0)),
                ('total_amt', models.FloatField(default=0, null=True)),
                ('food_date', models.CharField(max_length=50, null=True)),
            ],
        ),
    ]

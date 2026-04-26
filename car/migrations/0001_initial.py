# Generated migration

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Car model name', max_length=200)),
                ('brand', models.CharField(help_text='Brand name (e.g., BMW, Mercedes)', max_length=100)),
                ('price', models.DecimalField(decimal_places=2, help_text='Price in INR', max_digits=12)),
                ('fuel_type', models.CharField(choices=[('Petrol', 'Petrol'), ('Diesel', 'Diesel'), ('Electric', 'Electric'), ('Hybrid', 'Hybrid')], default='Petrol', max_length=20)),
                ('transmission', models.CharField(choices=[('Automatic', 'Automatic'), ('Manual', 'Manual')], default='Automatic', max_length=20)),
                ('model_year', models.IntegerField(help_text='Manufacturing year')),
                ('mileage', models.CharField(help_text='Mileage (e.g., 15 km/l)', max_length=50)),
                ('description', models.TextField(help_text='Detailed description of the car')),
                ('main_image', models.ImageField(help_text='Main display image', upload_to='cars/')),
                ('image1', models.ImageField(blank=True, null=True, upload_to='cars/')),
                ('image2', models.ImageField(blank=True, null=True, upload_to='cars/')),
                ('image3', models.ImageField(blank=True, null=True, upload_to='cars/')),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Luxury Car',
                'verbose_name_plural': 'Luxury Cars',
                'ordering': ['-date_added'],
            },
        ),
    ]

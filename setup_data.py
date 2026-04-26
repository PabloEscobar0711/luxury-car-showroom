
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luxury_car_showroom.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth import get_user_model
from car.models import Car
from decimal import Decimal

User = get_user_model()

# Sample car data
sample_cars = [
    {
        'name': '7 Series',
        'brand': 'BMW',
        'price': Decimal('14500000.00'),
        'fuel_type': 'Petrol',
        'transmission': 'Automatic',
        'model_year': 2024,
        'mileage': '12 km/l',
        'description': 'The BMW 7 Series represents the pinnacle of luxury sedans, combining cutting-edge technology with unmatched comfort. Features include adaptive LED headlights, premium leather interior, advanced driver assistance systems, and a powerful engine that delivers smooth performance.',
    },
    {
        'name': 'S-Class',
        'brand': 'Mercedes',
        'price': Decimal('16800000.00'),
        'fuel_type': 'Hybrid',
        'transmission': 'Automatic',
        'model_year': 2024,
        'mileage': '14 km/l',
        'description': 'The Mercedes-Benz S-Class sets the standard for luxury automobiles worldwide. Experience unparalleled comfort with AIRMATIC suspension, MBUX infotainment system, Burmester surround sound, and an interior crafted from the finest materials.',
    },
    {
        'name': 'A8 L',
        'brand': 'Audi',
        'price': Decimal('15200000.00'),
        'fuel_type': 'Diesel',
        'transmission': 'Automatic',
        'model_year': 2024,
        'mileage': '13 km/l',
        'description': 'The Audi A8 L combines sophisticated design with advanced technology. Features include Matrix LED headlights, Virtual Cockpit, quattro all-wheel drive, and an exceptionally spacious rear cabin with executive seating.',
    },
    {
        'name': 'Phantom',
        'brand': 'Rolls-Royce',
        'price': Decimal('95000000.00'),
        'fuel_type': 'Petrol',
        'transmission': 'Automatic',
        'model_year': 2024,
        'mileage': '8 km/l',
        'description': 'The Rolls-Royce Phantom is the ultimate expression of automotive luxury. Hand-crafted to perfection with bespoke interior options, whisper-quiet cabin, starlight headliner, and the legendary Rolls-Royce ride quality.',
    },
    {
        'name': '911 Turbo S',
        'brand': 'Porsche',
        'price': Decimal('28500000.00'),
        'fuel_type': 'Petrol',
        'transmission': 'Automatic',
        'model_year': 2024,
        'mileage': '10 km/l',
        'description': 'The Porsche 911 Turbo S is an icon of performance and luxury. With a twin-turbo flat-six engine producing 640 HP, it accelerates from 0-100 km/h in just 2.7 seconds while offering everyday usability and comfort.',
    },
    {
        'name': 'X7',
        'brand': 'BMW',
        'price': Decimal('12500000.00'),
        'fuel_type': 'Diesel',
        'transmission': 'Automatic',
        'model_year': 2024,
        'mileage': '11 km/l',
        'description': 'The BMW X7 is the ultimate luxury SUV, offering three rows of seating in supreme comfort. Features panoramic sky lounge roof, Bowers & Wilkins sound system, and commanding road presence.',
    },
    {
        'name': 'GLE',
        'brand': 'Mercedes',
        'price': Decimal('9800000.00'),
        'fuel_type': 'Petrol',
        'transmission': 'Automatic',
        'model_year': 2024,
        'mileage': '11 km/l',
        'description': 'The Mercedes-Benz GLE combines SUV versatility with sedan-like luxury. Equipped with E-ACTIVE BODY CONTROL, MBUX, and spacious interior with premium materials.',
    },
    {
        'name': 'Q8',
        'brand': 'Audi',
        'price': Decimal('10500000.00'),
        'fuel_type': 'Petrol',
        'transmission': 'Automatic',
        'model_year': 2024,
        'mileage': '10 km/l',
        'description': 'The Audi Q8 is a bold luxury SUV with coupe styling. Features include dual touchscreen MMI system, virtual cockpit plus, Bang & Olufsen sound, and dynamic all-wheel steering.',
    },
    {
        'name': 'Ghost',
        'brand': 'Rolls-Royce',
        'price': Decimal('65000000.00'),
        'fuel_type': 'Petrol',
        'transmission': 'Automatic',
        'model_year': 2024,
        'mileage': '9 km/l',
        'description': 'The Rolls-Royce Ghost delivers effortless performance with understated elegance. Features include the planar suspension system, illuminated fascia, and hand-crafted luxury throughout.',
    },
    {
        'name': 'Cayenne Turbo',
        'brand': 'Porsche',
        'price': Decimal('19500000.00'),
        'fuel_type': 'Hybrid',
        'transmission': 'Automatic',
        'model_year': 2024,
        'mileage': '12 km/l',
        'description': 'The Porsche Cayenne Turbo combines sports car performance with SUV practicality. Powered by a 4.0L V8 with 541 HP, it offers dynamic handling and luxurious comfort.',
    },
]

print("Creating superuser...")
try:
    if not User.objects.filter(username='adnan').exists():
        User.objects.create_superuser(
            username='adnan',
            email='adhasan07@gmail.com',
            password='adnan@123'
        )
        print("✅ Superuser 'adnan' created successfully!")
    else:
        print("✅ Superuser 'adnan' already exists!")
except Exception as e:
    print(f"Error creating superuser: {e}")

print("\nAdding sample cars...")
for car_data in sample_cars:
    try:
        car, created = Car.objects.get_or_create(
            name=car_data['name'],
            brand=car_data['brand'],
            defaults=car_data
        )
        if created:
            print(f"✅ Added: {car.brand} {car.name}")
        else:
            print(f"⚠️  Already exists: {car.brand} {car.name}")
    except Exception as e:
        print(f"Error adding {car_data['name']}: {e}")

print("\n✅ Database setup complete!")
print("\nTotal cars in database:", Car.objects.count())

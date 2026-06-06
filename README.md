# Luxury Car Showroom - Django Project

## 🚗 Premium Luxury Car Website

A fully functional Django website for a luxury car showroom featuring BMW, Mercedes-Benz, Audi, Rolls-Royce, and Porsche vehicles.

---

## 📋 Project Features

✅ **Modern Luxury UI** - Black + Gold + White premium theme
✅ **Car Management** - Complete CRUD operations via admin panel
✅ **Image Gallery** - Multiple images per car with gallery view
✅ **Filtering** - Filter cars by brand and fuel type
✅ **Responsive Design** - Works on mobile, tablet, and desktop
✅ **Pre-loaded Sample Data** - 10+ luxury cars with images
✅ **Admin Panel** - Fully configured Django admin

---

## 🛠️ Tech Stack

- **Backend:** Python + Django 4.2
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Database:** SQLite3 (pre-migrated)
- **Icons:** Font Awesome 6

---

## 📦 Installation Steps

### 1️⃣ Extract the ZIP file
```bash
unzip luxury_car_showroom.zip
cd luxury_car_showroom
```

### 2️⃣ Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Mac/Linux
python3 -m venv venv
source venv/bin/activate

## 📂 Project Structure

```
luxury_car_showroom/
│
├── luxury_car_showroom/       # Main project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── car/                       # Main app
│   ├── models.py             # Car model
│   ├── views.py              # All views
│   ├── urls.py               # URL routing
│   ├── admin.py              # Admin config
│   ├── templates/            # HTML templates
│   └── static/               # CSS, JS files
│
├── media/                    # Uploaded images
├── db.sqlite3               # Pre-migrated database
├── manage.py                # Django management
└── requirements.txt         # Dependencies
```

---

## 🎨 Features Overview

### 🏠 Homepage
- Luxury hero banner
- Featured cars showcase
- Why Choose Us section

### 🚘 Car Listing Page
- Grid view of all cars
- Filter by brand
- Filter by fuel type
- Pagination support

### 📋 Car Detail Page
- Large image gallery
- Complete specifications
- Related cars suggestions
- Contact for booking button

### 📞 Contact Page
- Contact form
- Location details
- Business hours

### ℹ️ About Page
- Company information
- Mission statement
- Brand showcase

---

## 🔧 How to Add New Cars

1. Login to admin panel: http://127.0.0.1:8000/admin/
2. Click on "Luxury Cars"
3. Click "Add Luxury Car"
4. Fill in all details
5. Upload images
6. Click "Save"

---

## 📱 Responsive Design

The website is fully responsive and works seamlessly on:
- 📱 Mobile phones
- 📱 Tablets
- 💻 Laptops
- 🖥️ Desktop computers

---

## 🎨 Color Theme

- **Primary:** Black (#0a0a0a)
- **Secondary:** Gold (#d4af37)
- **Accent:** White (#ffffff)
- **Style:** Royal Luxury Premium

---

## ⚙️ Configuration

The project uses SQLite database which is already included and pre-migrated. No additional setup needed!

If you want to reset the database:
```bash
# Delete db.sqlite3
# Then run:
python manage.py migrate
python manage.py createsuperuser
```

---

## 🚀 Deployment Tips

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Add your domain to `ALLOWED_HOSTS`
3. Configure static files properly
4. Use PostgreSQL instead of SQLite
5. Set up proper SECRET_KEY

---

## 📄 License

This project is created for educational purposes.

---

## 👨‍💻 Developer

Created with ❤️ for luxury car enthusiasts

---

## 🆘 Troubleshooting

**Issue:** Module not found
**Solution:** Make sure virtual environment is activated and dependencies are installed

**Issue:** Images not showing
**Solution:** Check MEDIA_ROOT and MEDIA_URL settings in settings.py

**Issue:** Admin login not working
**Solution:** Use credentials: adnan / adnan@123

---

## 📞 Support

For any issues or questions, please contact through the admin panel or raise an issue.

---

**Enjoy your Luxury Car Showroom! 🚗✨**

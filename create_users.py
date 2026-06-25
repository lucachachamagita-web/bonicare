import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myHospital.settings')
django.setup()

from django.contrib.auth.models import User

users = ['receptionist', 'doctor', 'patient', 'labattendant']
password = 'qwerty123'

for username in users:
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(username=username, password=password)
        print(f"Created user: {username}")
    else:
        print(f"User {username} already exists.")

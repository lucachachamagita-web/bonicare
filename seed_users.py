import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myHospital.settings')
django.setup()

from django.contrib.auth.models import User
from profiles.models import UserProfile

def create_user(username, password, email, role):
    if not User.objects.filter(username=username).exists():
        u = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=u, role=role, phone='1234567890')
        print(f"Created {role} user: {username} / {password}")
    else:
        print(f"User {username} already exists.")

print("Seeding default users...")
create_user('wekesa', 'Wekesa@123', 'admin@clinic.com', 'PROPRIETOR')
create_user('test_doctor', 'testpass123', 'doc@clinic.com', 'DOCTOR')
create_user('test_attendant', 'testpass123', 'attendant@clinic.com', 'ATTENDANT')

# Make the proprietor a superuser too for admin access
admin_user = User.objects.get(username='wekesa')
admin_user.is_superuser = True
admin_user.is_staff = True
admin_user.save()
print("Seeding complete.")

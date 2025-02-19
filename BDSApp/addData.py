import os
import django

# Cấu hình Django trước khi import model
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BDSProject.settings')
django.setup()
from BDSApp.models import Apartment

apartment1 = Apartment.objects.create(
    building_name="Tòa nhà A",
    address="123 Đường ABC, TP.HCM",
    room_count=3,
    price_per_month=15000000,
    price_per_day=500000,
    available=True,
    image="images/apartment1.png",
    description="Căn hộ rộng rãi, tiện nghi"
)

apartment2 = Apartment.objects.create(
    building_name="Tòa nhà B",
    address="456 Đường XYZ, Hà Nội",
    room_count=2,
    price_per_month=12000000,
    price_per_day=400000,
    available=False,
    image="images/apartment1.png",
    description="Gần trung tâm, có bể bơi"
)

print("Dữ liệu đã được thêm thành công!")

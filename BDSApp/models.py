from django.db import models

class Building(models.Model):
    image = models.ImageField(upload_to='buildings/', blank=True, null=True)  # Sử dụng ImageField
    name = models.CharField(max_length=255)  # Tên tòa nhà
    address = models.TextField()  # Địa chỉ

    def __str__(self):
        return self.name

class Apartment(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="apartments")  # Tòa nhà chứa căn hộ
    floor = models.IntegerField(null=True, blank=True)  # Tầng
    room_name = models.CharField(max_length=255, null=True, blank=True)  # Tên phòng
    price_per_day = models.IntegerField(null=True, blank=True)  # Giá thuê theo ngày
    price_per_month = models.IntegerField(null=True, blank=True)  # Giá thuê theo tháng
    available = models.BooleanField(default=True)  # Trạng thái phòng
    image = models.ImageField(upload_to='apartments/', blank=True, null=True)  # Sử dụng ImageField
    description = models.TextField(null=True, blank=True)  # Mô tả

    def __str__(self):
        return f"{self.room_name} - Tầng {self.floor} - {self.building.name}"

class Customer(models.Model):
    full_name = models.CharField(max_length=255)  # Họ tên
    cccd = models.CharField(max_length=12, unique=True)  # Căn cước công dân
    phone = models.CharField(max_length=15, null=True, blank=True)  # Số điện thoại
    email = models.EmailField(null=True, blank=True)  # Email

    def __str__(self):
        return self.full_name

class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="bookings")  # Khách hàng đặt phòng
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="bookings")  # Phòng được đặt
    date_check_in = models.DateField()  # Ngày nhận phòng
    date_check_out = models.DateField()  # Ngày trả phòng

    class Meta:
        unique_together = ('apartment', 'date_check_in', 'date_check_out')  # Đảm bảo không có trùng lịch đặt

    def __str__(self):
        return f"{self.customer.full_name} đặt {self.apartment.room_name} từ {self.date_check_in} đến {self.date_check_out}"

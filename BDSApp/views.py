from django.shortcuts import render,redirect
from .models import Customer, Booking, Apartment,Building
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect


# Create your views here.
def home(request):
    query = request.GET.get('q', '')
    building_id = request.GET.get('building', '')  # Lấy ID tòa nhà từ URL
    apartments = Apartment.objects.all()

    if query:
        apartments = apartments.filter(room_name__icontains=query)
    if building_id:
        apartments = apartments.filter(building_id=building_id)

    apartments = apartments.order_by("-id")  # Sắp xếp theo ID giảm dần (căn hộ mới nhất lên đầu)

    paginator = Paginator(apartments, 3)  # Mỗi trang 3 căn hộ
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)  # Lấy danh sách căn hộ của trang hiện tại

    buildings = Building.objects.all()  # Lấy danh sách tất cả tòa nhà

    return render(request, 'home.html', {
        'apartments':apartments,
        'page_obj': page_obj,
        'query': query,
        'buildings': buildings,
        'selected_building': building_id,  # Để giữ trạng thái dropdown
    })

@csrf_exempt  # Nếu dùng fetch API thì cần cái này, hoặc gửi CSRF Token từ front-end
def delete_apartment(request, apartment_id):
    if request.method == "DELETE":
        try:
            apartment = Apartment.objects.get(id=apartment_id)
            apartment.delete()
            return JsonResponse({"success": True, "message": "Xóa thành công!"})
        except Apartment.DoesNotExist:
            return JsonResponse({"success": False, "message": "Căn hộ không tồn tại."})
    
    return JsonResponse({"success": False, "message": "Phương thức không hợp lệ."})


def add_apartment(request):
    if request.method == "POST":
        try:
            room_name = request.POST.get("room_name")
            floor = request.POST.get("floor")
            price_per_day = request.POST.get("price_per_day")
            price_per_month = request.POST.get("price_per_month")
            description = request.POST.get("description")
            building_id = request.POST.get("building")
            image_file = request.FILES.get("image")  # Lấy file ảnh
            # Kiểm tra building có tồn tại không
            building = Building.objects.get(id=building_id)

            # Nếu có ảnh, lưu vào BDSApp/static/images/
            image_path = None
            if image_file:
                # File image sẽ được lưu vào thư mục MEDIA_ROOT/apartments/
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                filename = fs.save(image_file.name, image_file)  # Lưu ảnh vào media/apartments/
                image_path = filename  # Đường dẫn sẽ được lưu vào cơ sở dữ liệu


            # Tạo căn hộ mới
            apartment = Apartment.objects.create(
                room_name=room_name,
                floor=floor,
                price_per_day=price_per_day,
                price_per_month=price_per_month,
                description=description,
                building=building,
                image=image_path  # Lưu đường dẫn ảnh
            )

            return JsonResponse({"status": "success", "apartment_id": apartment.id})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@csrf_exempt  # Đảm bảo rằng CSRF token được bỏ qua cho việc thử nghiệm hoặc nếu bạn đã sử dụng CSRF token trong JavaScript
def update_apartment(request, apartment_id):
    if request.method == "POST":
        try:
            # Lấy căn hộ cần cập nhật
            apartment = Apartment.objects.get(id=apartment_id)

            # Cập nhật các trường dữ liệu từ form
            apartment.room_name = request.POST.get("room_name")
            apartment.floor = request.POST.get("floor")
            apartment.price_per_day = request.POST.get("price_per_day")
            apartment.price_per_month = request.POST.get("price_per_month")
            apartment.description = request.POST.get("description")
            apartment.building_id = request.POST.get("building")

            # Kiểm tra xem có ảnh mới không và cập nhật ảnh nếu có
            if "image" in request.FILES:
                image_file = request.FILES["image"]
                # Lưu ảnh vào thư mục media
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                filename = fs.save(image_file.name, image_file)
                apartment.image = filename  # Lưu tên tệp ảnh vào trường image

            # Lưu lại căn hộ sau khi cập nhật
            apartment.save()

            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


def rental_management(request):
    query = request.GET.get('q', '')  # Lấy từ khóa tìm kiếm
    status = request.GET.get('status', '')  # Lấy trạng thái từ URL
    apartments = Apartment.objects.all()

    # Lọc theo tên phòng nếu có nhập từ khóa
    if query:
        apartments = apartments.filter(room_name__icontains=query)

    # Lọc theo trạng thái
    if status == "available":
        apartments = apartments.filter(available=True)  # Còn trống
    elif status == "rented":
        apartments = apartments.filter(available=False)  # Đã thuê

    # Sắp xếp căn hộ theo ID giảm dần
    apartments = apartments.order_by("-id")

    # Phân trang: Mỗi trang hiển thị 3 căn hộ
    paginator = Paginator(apartments, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'rental_management.html', {
        'page_obj': page_obj,
        'query': query,
        'selected_status': status,  # Giữ trạng thái dropdown
    })

@csrf_exempt
def create_booking(request):
    if request.method == "POST":
        try:
            customer_name = request.POST.get("customer_name")
            phone_number = request.POST.get("phone_number")
            email = request.POST.get("email")
            id_card = request.POST.get("id_card")
            booking_type = request.POST.get("booking_type")
            date_check_in = request.POST.get("date_check_in")
            date_check_out = request.POST.get("date_check_out")
            apartment_id = request.POST.get("apartment_id")

            # Lấy hoặc tạo khách hàng mới
            customer, created = Customer.objects.get_or_create(
                cccd=id_card,
                defaults={
                    "full_name": customer_name,
                    "phone": phone_number,
                    "email": email,
                }
            )

            # Lấy căn hộ
            apartment = Apartment.objects.get(id=apartment_id)

            # Tạo booking
            booking = Booking.objects.create(
                customer=customer,
                apartment=apartment,
                date_check_in=date_check_in,
                date_check_out=date_check_out if booking_type == "daily" else None
            )

            # Cập nhật trạng thái phòng thành đã thuê
            apartment.available = False
            apartment.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request"})

def get_customer_by_apartment(request, apartment_id):
    try:
        booking = Booking.objects.get(apartment_id=apartment_id)
        customer = booking.customer

        return JsonResponse({
            "success": True,
            "customer": {
                "id": customer.id,
                "full_name": customer.full_name,
                "phone": customer.phone,
                "email": customer.email,
                "cccd": customer.cccd,
            },
            "booking": {
                "type": "daily" if booking.date_check_out else "monthly",
                "date_check_in": str(booking.date_check_in),
                "date_check_out": str(booking.date_check_out),
            },
            "price_per_day": booking.apartment.price_per_day,
            "price_per_month": booking.apartment.price_per_month
        })
    except Booking.DoesNotExist:
        return JsonResponse({"success": False, "error": "Không tìm thấy khách hàng!"})
    
@csrf_exempt
def update_customer(request):
    if request.method == "POST":
        try:
            data = request.POST
            customer_id = data.get("customer_id")
            customer = Customer.objects.get(id=customer_id)

            customer.full_name = data.get("customer_name")
            customer.phone = data.get("phone_number")
            customer.email = data.get("email")
            customer.cccd = data.get("id_card")
            customer.save()

            booking = Booking.objects.get(customer=customer)
            booking.date_check_in = data.get("date_check_in")
            booking.date_check_out = data.get("date_check_out")
            booking.save()

            return JsonResponse({"success": True})
        except Customer.DoesNotExist:
            return JsonResponse({"success": False, "error": "Khách hàng không tồn tại!"})
        except Booking.DoesNotExist:
            return JsonResponse({"success": False, "error": "Booking không tồn tại!"})

    return JsonResponse({"success": False, "error": "Phương thức không hợp lệ!"})    

@csrf_exempt
def delete_booking(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            customer_id = data.get("customer_id")
            apartment_id = data.get("apartment_id")

            booking = Booking.objects.get(customer_id=customer_id, apartment_id=apartment_id)
            booking.delete()

            # Cập nhật trạng thái phòng trống
            Apartment.objects.filter(id=apartment_id).update(available=True)

            return JsonResponse({"success": True})
        except Booking.DoesNotExist:
            return JsonResponse({"success": False, "error": "Không tìm thấy booking!"})

    return JsonResponse({"success": False, "error": "Phương thức không hợp lệ!"})

def building(request):
    buildings = Building.objects.all()
    paginator = Paginator(buildings, 3)  # Mỗi trang hiển thị 5 tòa nhà
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'building.html', {'page_obj': page_obj})

@csrf_exempt
def add_building(request):
    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        image = request.FILES.get("image")  # Lấy file ảnh nếu có

        if not name or not address:
            return JsonResponse({"success": False, "error": "Thiếu thông tin cần thiết!"})

        building = Building(name=name, address=address, image=image)
        building.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Phương thức không hợp lệ!"})

@csrf_exempt
def edit_building(request):
    if request.method == "POST":
        building_id = request.POST.get("building_id")
        name = request.POST.get("name")
        address = request.POST.get("address")
        image = request.FILES.get("image")  # Lấy file ảnh nếu có

        try:
            building = Building.objects.get(id=building_id)
            building.name = name
            building.address = address
            if image:
                building.image = image
            building.save()
            return JsonResponse({"success": True})
        except Building.DoesNotExist:
            return JsonResponse({"success": False, "error": "Tòa nhà không tồn tại!"})

    return JsonResponse({"success": False, "error": "Phương thức không hợp lệ!"})

def delete_building(request, building_id):
    building = get_object_or_404(Building, id=building_id)

    # Kiểm tra nếu tòa nhà còn căn hộ
    if building.apartments.exists():
        return redirect('building')  # Chuyển về danh sách tòa nhà

    # Nếu không có căn hộ, cho phép xóa
    building.delete()
    return redirect('building')

@csrf_exempt
def delete_customer(request, apartment_id):
    if request.method == "POST":
        try:
            # Tìm tất cả khách hàng đã đặt căn hộ này
            customers_to_delete = Customer.objects.filter(bookings__apartment_id=apartment_id).distinct()

            # Xóa Booking liên quan trước
            Booking.objects.filter(apartment_id=apartment_id).delete()


            # Xóa khách hàng
            customers_to_delete.delete()
            apartment = get_object_or_404(Apartment, id=apartment_id)
            if not Booking.objects.filter(apartment=apartment).exists():
                apartment.available = True
                apartment.save()

            return JsonResponse({"success": True}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Phương thức không hợp lệ"}, status=400)
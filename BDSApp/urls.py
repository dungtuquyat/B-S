from django.urls import path
from .views import home
from .views import delete_apartment,add_apartment,update_apartment,rental_management,create_booking,building,add_building
from .views import get_customer_by_apartment, update_customer, delete_booking,edit_building,delete_building,delete_customer

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path("delete-apartment/<int:apartment_id>/", delete_apartment, name="delete_apartment"),
    path("add-apartment/", add_apartment, name="add_apartment"),
    path("update-apartment/<int:apartment_id>/", update_apartment, name="update_apartment"),
    path('rental/', rental_management, name='rental_management'),
    path('building/', building, name='building'),
    path('delete-building/<int:building_id>/', delete_building, name='delete_building'),
    path("create_booking/", create_booking, name="create_booking"),
    path('get_customer_by_apartment/<int:apartment_id>/', get_customer_by_apartment, name='get_customer_by_apartment'),
    path('update_customer/', update_customer, name='update_customer'),
    path('delete_booking/', delete_booking, name='delete_booking'),
    path('add-building/', add_building, name='add_building'),
    path('edit-building/', edit_building, name='edit_building'),
    path('delete-customer/<int:apartment_id>/', delete_customer, name='delete_customer'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from .models import Student, Employee, Hostel, Payment, Transcation, Room, Booking

# Register your models here.
admin.site.register(Student)
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(Hostel)
admin.site.register(Employee)
admin.site.register(Payment)
admin.site.register(Transcation)

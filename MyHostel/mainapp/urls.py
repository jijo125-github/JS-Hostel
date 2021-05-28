from django.urls import path
from .views import (
        createHostelView, 
        CreateEmployee, 
        GetHostelDetails, 
        getStudentFromHostel, 
        GetVacantRooms, 
        CreateStudentDetails, 
        DoBooking
    )

urlpatterns = [
    path('createHostel/', createHostelView, name='Create_Hostel'),
    path('createEmployee/', CreateEmployee.as_view(), name='Create_Employee'),
    path('getVacantRooms/', GetVacantRooms.as_view(), name='List_Vacant_Rooms'),
    path('getHostelDetails/<int:pk>/', GetHostelDetails.as_view(),name='Get_Particular_Hostel_Details'),
    path('getStudents/<int:pk>/',getStudentFromHostel, name='Get_Students_Name_From_Hostel'),
    path('createStudent/', CreateStudentDetails.as_view(),name='Create_Student'),
    path('booking/', DoBooking.as_view(),name='Do_Booking'),
    path('booking/<int:pk>/', DoBooking.as_view(), name='Get_Booking_Details')
]

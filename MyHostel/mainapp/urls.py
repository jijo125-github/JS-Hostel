from django.urls import path
from .views import (
        createHostelView, 
        CreateEmployee,
        GetEmployee,
        ListEmployee, 
        GetHostelDetails, 
        getStudentFromHostel,
        create_room, 
        GetVacantRooms, 
        CreateStudentDetails, 
        DoBooking
    )

urlpatterns = [
    path('createHostel/', createHostelView, name='Create_Hostel'),
    path('getHostelDetails/<int:pk>/', GetHostelDetails.as_view(),name='Get_Particular_Hostel_Details'),
    path('createEmployee/', CreateEmployee.as_view(), name='Create_Employee'),
    path('getEmployee/<int:pk>/', GetEmployee.as_view(), name='Get_Employee'),
    path('listEmployee/', ListEmployee.as_view(), name='List_Employee'),
    path('createRoom/', create_room, name='Create_Room'),
    path('getVacantRooms/', GetVacantRooms.as_view(), name='List_Vacant_Rooms'),
    path('createStudent/', CreateStudentDetails.as_view(),name='Create_Student'),
    path('getStudents/<int:pk>/',getStudentFromHostel, name='Get_Students_Name_From_Hostel'),
    path('booking/', DoBooking.as_view(),name='Do_Booking'),
    path('booking/<int:pk>/', DoBooking.as_view(), name='Get_Booking_Details')
]

from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import Student, Employee, Hostel, Payment, Transcation, Room, Booking
from .serializers import CreateEmployeeSerializer, CreateHostelSerializer, RoomSerializer
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import status


# Create your api views here.

@api_view(['POST'])
def createHostelView(request):
    """ Admin create details of Hostel in this view """
    serialized_data = CreateHostelSerializer(data=request.data)
    try:
        if serialized_data.is_valid(raise_exception=True):
            hostel_serialized_data = serialized_data.validated_data
            hos_name = hostel_serialized_data.get('name')
            hos_address = hostel_serialized_data.get('address')
            hos_phone_no = hostel_serialized_data.get('phone_no')
            hos_manager_id = hostel_serialized_data.get('manager_id')
            hosobj = Hostel(name=hos_name, address=hos_address, phone_no=hos_phone_no, manager_id=hos_manager_id)
            hosobj.save()
            
            data = {
                'savedToDatabase' : True
            }
    except:
        data = {
            'savedToDatabase' : False,
            'error' : 'some error has occured in saving the details'
        }
    return JsonResponse(data, status=status.HTTP_201_CREATED)


class CreateEmployee(CreateAPIView):
    """ Admin shall create the main employee details """
    serializer_class = CreateEmployeeSerializer

    def create(self, request, *args, **kwargs):
        try:
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')

            if Employee.objects.filter(first_name=first_name, last_name=last_name).exists():
                raise ValidationError({'error' : 'Employee already created'})
            else:
                return super().create(request, *args, **kwargs)  
        except:
            data = {
                "Failed": True,
                "error" : "Employee already exists"
            } 
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class GetHostelDetails(RetrieveAPIView):
    """ Get the particular hostel details """
    queryset = Hostel.objects.all()
    serializer_class = CreateHostelSerializer


@api_view(['GET'])
def getStudentFromHostel(request, pk):
    """ to get the names of students who have booked a hostel """
    try:
        rooms = Room.objects.filter(hostel=pk)
        if rooms.count() == 0:
            raise ObjectDoesNotExist
        data = {
            'message' : 'There are no students in this hostel'
            }
        student_names = list()
        for room in rooms:
            booking_qs = Booking.objects.filter(room=room)
            if booking_qs:
                for booking_obj in booking_qs:
                    full_name = booking_obj.student.full_name
                    student_names.append(full_name)           
        if len(student_names) > 0:
            data = {
                'student_full_names_list' : student_names,
                'message' : f'got {len(student_names)} students'
            }
        return JsonResponse(data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        data = {
            'error_message' : 'hostel object does not exist. Please pass correct hostel obj request' 
        }
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


class RoomsPagination(LimitOffsetPagination):
    """ paginating rooms """
    default_limit = 2
    max_limit = 10


class GetVacantRooms(ListAPIView):
    """ Api to get all vacant rooms available """
    queryset = Room.objects.filter(status='vacant')
    serializer_class = RoomSerializer
    pagination_class = RoomsPagination


class CreateStudentDetails(CreateAPIView):
    """ Api to create student details """
    pass
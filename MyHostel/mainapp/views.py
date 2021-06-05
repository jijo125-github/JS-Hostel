from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import status
from .models import Student, Employee, Hostel, Payment, Transcation, Room, Booking
from .serializers import (
    CreateEmployeeSerializer,
    EmployeeSerializer, 
    CreateHostelSerializer, 
    GetBookingSerializer, 
    RoomSerializer, 
    StudentSerializer, 
    BookingSerializer,
    CreatePaymentSerializer,
    PaymentSerializer
)


# Create your api views here.

class ModelsPagination(LimitOffsetPagination):
    """ paginating models """
    default_limit = 2
    max_limit = 10


@api_view(['POST'])
def createHostelView(request):
    """ Admin create details of Hostel in this view """

    createHostelDataFormat = {
        "name": "Test ABC",
        "address": "Bhavnath Bangalore",
        "phone_no": "9991231231",
        "manager_id": "1",
        "room_limit" : "40"
    }
    
    try:
        serialized_data = CreateHostelSerializer(data=request.data)
        if serialized_data.is_valid(raise_exception=True):
            hostel_serialized_data = serialized_data.validated_data
            hos_name = hostel_serialized_data.get('name')
            hos_address = hostel_serialized_data.get('address')
            hos_phone_no = hostel_serialized_data.get('phone_no')
            hos_manager_id = hostel_serialized_data.get('manager_id')
            hos_room_limit = hostel_serialized_data.get('room_limit')
            hosobj = Hostel(
                name=hos_name, 
                address=hos_address, 
                phone_no=hos_phone_no, 
                manager_id=hos_manager_id, 
                room_limit=hos_room_limit
                )
            hosobj.save()
            data = {
                'savedToDatabase' : True
            }
            return JsonResponse(data, status=status.HTTP_201_CREATED)
    except:
        errordata = {
            'savedToDatabase' : False,
            'error' : 'some error has occured in saving the details'
        }
        return JsonResponse(errordata, status=status.HTTP_400_BAD_REQUEST)
    

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


class GetEmployee(RetrieveAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class ListEmployee(ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    pagination_class = ModelsPagination
    filter_backends = (OrderingFilter,)
    ordering_fields = ('first_name',)

    def get_queryset(self):
        """ get the list of employees from a hostel """
        hostel_name = self.request.query_params.get('hostel', None)
        if hostel_name is None:
            return super().get_queryset()
        queryset = Employee.objects.filter(hostel__name=hostel_name)
        if queryset.exists():
            return queryset
        raise ValidationError('Hostel name is incorrect or hostel doesnt exist with name')


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
        raise ValidationError({
            'error_message' : 'hostel object does not exist. Please pass correct hostel obj request' 
        })


@api_view(['POST'])
def create_room(request):
    """ view to create Room """

    createRoomDataFormat = {
        "hostel": "1",
        "description": "King Sized Bedroom",
        "price": "3000",
        "status": "vacant"
    }

    serializer = RoomSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        response_data = serializer.data.copy()
        extra_data = {
            'created' : True,
            'hostel_name' : Hostel.objects.get(hostel_branch_id=response_data.get('hostel')).name
        }
        response_data.pop('hostel')
        response_data.update(extra_data)
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response({
        'failed' : True
        }, status=status.HTTP_400_BAD_REQUEST)

   
class GetVacantRooms(ListAPIView):
    """ Api to get all vacant rooms available """
    queryset = Room.objects.filter(status='vacant')
    serializer_class = RoomSerializer
    pagination_class = ModelsPagination

    def get_queryset(self):
        """ Raise error message if no rooms are available """
        if self.queryset.count() == 0:
            raise ValidationError({
                'room-count' : 0,
                'error' : 'Sorry, all rooms are occupied. Please try later..'
                })

        """ filter rooms under a specific price limit """
        room_price_limit = self.request.query_params.get('price_limit', None)
        if not room_price_limit:
            return super().get_queryset()
        queryset = Room.objects.filter(status='vacant').filter(price__lte=room_price_limit)
        if queryset.exists():
            return queryset
        raise ValidationError(f'There are no vacant rooms below {room_price_limit}')
        
        
class CreateStudentDetails(CreateAPIView):
    """ Api to create student details """
    serializer_class = StudentSerializer

    def create(self, request, *args, **kwargs):
        """ do not create if student exists """
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        if Student.objects.filter(first_name=first_name, last_name=last_name).exists():
            errordata = {
            "Failed": True,
            "error" : "Student already exists"
        }
            raise ValidationError(errordata, code=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
          

class DoBooking(APIView):
    """ Book a room """

    dobookingDataFormat = {
        "student": "1",
        "room": "2",
        "check_in_date": "2021-05-19",
        "check_out_date": "2021-05-23"
    }

    def post(self, request):
        """ only allow to book if serialized data validated """
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            booking_data = serializer.validated_data
            booking_obj = Booking(
                student         = booking_data.get('student'),
                room            = booking_data.get('room'),
                check_in_date   = booking_data.get('check_in_date'),
                check_out_date  = booking_data.get('check_out_date')
            )
            booking_obj.save()
            response_data = serializer.data
            response_data.update({
                'created' : True,
                'no_of_nights' : (booking_data.get('check_out_date') - booking_data.get('check_in_date')).days,
                'room_status' : 'Reserved'
                })
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_object(self):
        """ Get booking object by id """
        try:
            id = self.kwargs.get('pk')
            return Booking.objects.get(booking_id = id)
        except ObjectDoesNotExist:
            error_data = {
                'failed' : True,
                'error' : 'Object Does not exist'
            }
            raise ValidationError(error_data)

    def get(self, request, *args, **kwargs):
        """ Get all booking details """
        booking = self.get_object()
        serializer = GetBookingSerializer(booking)
        return Response(serializer.data, status = status.HTTP_200_OK)


class PaymentView(APIView):
    """ payment details"""
    
    payment_format = {
        "student" : "4",
        "booking" : "20",
        "payment_mode" : "online"
    }

    def post(self, request, *args, **kwargs):
        """ create the payment details """ 
        serializer = CreatePaymentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_object(self):
        """ Get payment object by id """
        try:
            id = self.kwargs.get('pk')
            return Payment.objects.get(payment_id = id)
        except ObjectDoesNotExist:
            error_data = {
                'failed' : True,
                'error' : 'Object Does not exist'
            }
            raise ValidationError(error_data)
    
    def get(self, request, *args, **kwargs):
        """ get the payment details """
        payment = self.get_object()
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status = status.HTTP_200_OK)

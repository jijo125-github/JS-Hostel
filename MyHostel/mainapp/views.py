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
from .models import Student, Employee, Hostel, Payment, Room, Booking
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
    
    serializer = CreateHostelSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        hostel_serialized_data = serializer.validated_data
        hostel_serialized_data.save()
        data = {
            'hostelCreated' : True,
            'savedToDatabase' : True
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
    
    def get_queryset(self):
        """ Get booking queryset by id """
        try:
            bookings_qs = Booking.objects.all()
            id = self.kwargs.get('pk', None)
            """ return all bookings if no pk passed """
            if id is None:
                return bookings_qs    
            """ return the booking object if valid pk is present else raise error"""    
            booking_qs = bookings_qs.filter(booking_id = id)
            if booking_qs.exists() and booking_qs.count() > 1:
                raise ValidationError('Duplicate ids exist. Please look into it')
            if not booking_qs.exists():
                raise ObjectDoesNotExist
            return booking_qs
        except ObjectDoesNotExist:
            error_data = {
                'failed' : True,
                'error' : 'Object Does not exist'
            }
            raise ValidationError(error_data)

    def get(self, request, *args, **kwargs):
        """ Get all booking details """
        booking_qs = self.get_queryset()
        if booking_qs.count() > 1:
            room_price_limit = self.request.query_params.get('price_limit', None)
            if room_price_limit:
                booking_qs = booking_qs.filter(room__price__lte = int(room_price_limit))
        serializer = GetBookingSerializer(booking_qs, many=True)      
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        """ update booking details if any typo error """
        try:
            booking_id = self.kwargs.get('pk', None)
            if booking_id is None:
                raise ValidationError('empty parameter passed. Invalid')
            updated_booking_data = request.data
            booking_instance = Booking.objects.get(booking_id=booking_id)
            serializer = BookingSerializer(instance=booking_instance, data=updated_booking_data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            response_data = serializer.data 
            response_data.update({
                'updated' : True,
                'no_of_nights' : (serializer.validated_data.get('check_out_date') - serializer.validated_data.get('check_in_date')).days,
                'room_status' : 'Reserved'
                })
            return Response(response_data, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            raise ValidationError({
                'failed' : True,
                'error' : 'Object Does not exist'
                }, code=status.status.HTTP_400_BAD_REQUEST)


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
    
    def get_queryset(self):
        """ Get paying queryset by id """
        try:
            payment_qs = Payment.objects.all()
            id = self.kwargs.get('pk', None)
            """ return all payments done if no pk passed """
            if id is None:
                return payment_qs    
            """ return the payment object if valid pk is present else raise error"""    
            payment_qs = payment_qs.filter(payment_id = id)
            if payment_qs.exists() and payment_qs.count() > 1:
                raise ValidationError('Duplicate ids exist. Please look into it')
            if not payment_qs.exists():
                raise ObjectDoesNotExist
            return payment_qs
        except ObjectDoesNotExist:
            error_data = {
                'failed' : True,
                'error' : 'Object Does not exist'
            }
            raise ValidationError(error_data)
    
    def get(self, request, *args, **kwargs):
        """ get the payment details """
        payment = self.get_queryset()
        serializer = PaymentSerializer(payment, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)

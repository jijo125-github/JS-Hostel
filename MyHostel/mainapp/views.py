from django.shortcuts import render
from django.http import JsonResponse
from .models import Student, Employee, Hostel, Payment, Transcation, Room, Booking
from .serializers import CreateEmployeeSerializer, CreateHostelSerializer
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status


# Create your api views here.

@api_view(['POST'])
def createHostelView(request):
    """ Admin create details of Hostel in this view """
    serialized_data = CreateHostelSerializer(data=request.data)
    try:
        if serialized_data.is_valid(raise_exception=True):
            hostel_serialized_data = serialized_data.validated_data
            # print(hostel_serialized_data)
            hos_name = hostel_serialized_data.get('name')
            hos_address = hostel_serialized_data.get('address')
            hos_phone_no = hostel_serialized_data.get('phone_no')
            hos_manager_id = hostel_serialized_data.get('manager_id')
            hosobj = Hostel(name=hos_name, address=hos_address, phone_no=hos_phone_no, manager_id=hos_manager_id)
            hosobj.save()
            
            data = {
                'hostel_name' : hos_name,
                'hostel_address' : hos_address,
                'hostel_phone_no' : hos_phone_no,
                'hostel_manager_id' : hos_manager_id
            }
    except:
        data = {
            'error' : 'some error'
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
    
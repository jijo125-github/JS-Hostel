from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import Student, Employee, Hostel, Payment, Transcation, Room, Booking


# create your serializers here
class CreateEmployeeSerializer(serializers.ModelSerializer):
    phone_no = serializers.RegexField("^0?[6-9]\d{9}$")
    email_address = serializers.EmailField()

    class Meta:
        model = Employee
        fields = ('employee_id', 'first_name', 'last_name', 'address', 'phone_no', 'email_address', 'hostel')


class CreateHostelSerializer(serializers.ModelSerializer):
    phone_no = serializers.RegexField("^0?[6-9]\d{9}$")
    manager_id = serializers.IntegerField()

    class Meta:
        model = Hostel
        fields = ('name', 'address', 'phone_no', 'manager_id')


class StudentSerializer(serializers.ModelSerializer):
    hostel = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ('__all__', 'hostel',)
    
    def get_hostel(self, instance):
        pass


class RoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = '__all__'


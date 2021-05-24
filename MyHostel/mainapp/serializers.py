from rest_framework import serializers
from rest_framework.exceptions import ValidationError
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

    class Meta:
        model = Student
        fields = '__all__'
    

class RoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField()

    class Meta:
        model = Booking
        fields = ('student', 'room', 'check_in_date', 'check_out_date')

    def validate(self, data):
        """ validate: 
                check_out_date > check_in date,
                is room vacant?
         """
        if data['check_in_date'] > data['check_out_date']:
            raise ValidationError({"date-error" : "check_out_date should come after check_in_date."})
        room_id = data['room'].room_id
        room_vacant = Room.objects.get(room_id = room_id).is_room_vacant()
        if not room_vacant:
            raise ValidationError({'room-status' : 'Room is not vacant'})
        return data

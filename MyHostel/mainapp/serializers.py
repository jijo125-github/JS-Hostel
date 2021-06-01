from rest_framework import serializers
from .models import Student, Employee, Hostel, Payment, Transcation, Room, Booking


# create your serializers here
class CreateEmployeeSerializer(serializers.ModelSerializer):
    """ serializer to create employee details """
    phone_no = serializers.RegexField("^0?[6-9]\d{9}$")
    email_address = serializers.EmailField()

    class Meta:
        model = Employee
        fields = ('employee_id', 'first_name', 'last_name', 'address', 'phone_no', 'email_address', 'hostel')


class EmployeeSerializer(serializers.ModelSerializer):
    """ serializer to display or list out employee details """
    phone_no = serializers.RegexField("^0?[6-9]\d{9}$")
    email_address = serializers.EmailField()
    hostel = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = Employee
        fields = ('employee_id', 'full_name', 'address', 'phone_no', 'email_address', 'hostel')


class CreateHostelSerializer(serializers.ModelSerializer):
    phone_no = serializers.RegexField("^0?[6-9]\d{9}$")
    manager_id = serializers.IntegerField()

    class Meta:
        model = Hostel
        fields = ('name', 'address', 'phone_no', 'manager_id')


class StudentSerializer(serializers.ModelSerializer):
    """ serialize student data """

    class Meta:
        model = Student
        fields = ('first_name', 'last_name', 'address', 'phone_no')
    
    def validate_phone_no(self, value):
        if Student.objects.filter(phone_no = value).exists():
            raise serializers.ValidationError({"error":"This phone number already exists"})
        return value
    

class RoomSerializer(serializers.ModelSerializer):
    """ serialize the room details """

    class Meta:
        model = Room
        fields = ('__all__')

    def validate_price(self, value):
        """ room price neither can be null nor lesser than 0 """
        if value is None:
            raise serializers.ValidationError('Price cannot be null')
        elif value <= 0:
            raise serializers.ValidationError('Price cannot be lesser than 0')
        return value


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
            raise serializers.ValidationError({"date-error" : "check_out_date should come after check_in_date."})
        room_id = data['room'].room_id
        room_vacant = Room.objects.get(room_id = room_id).is_room_vacant()
        if not room_vacant:
            raise serializers.ValidationError({
                'room-status' : 'Room is not vacant',
                'failed' : True
                })
        return data


class GetBookingSerializer(serializers.ModelSerializer):
    """ Get the booking details of a particular booking """
    student = serializers.SlugRelatedField(read_only=True, slug_field='full_name')
    room = serializers.SlugRelatedField(read_only=True, slug_field='description')
    roomprice = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_status(self,obj):
        """ get room status """
        return obj.room.status
    
    def get_roomprice(self, obj):
        """ get room price """
        return obj.room.price


    class Meta:
        model = Booking
        fields = ('booking_id','student','room','roomprice','status','booking_date','check_in_date','check_out_date','no_of_nights')


class CreatePaymentSerializer(serializers.ModelSerializer):
    """ while doing payment serialize payment details """

    class Meta:
        model = Payment
        fields = ('payment_id', 'student', 'booking', 'payment_mode')
    
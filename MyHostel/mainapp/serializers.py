from rest_framework import serializers
from .models import Student, Employee, Hostel, Payment, Transcation, Room, Booking


# create your serializers here
class CreateEmployeeSerializer(serializers.ModelSerializer):
    """ serializer to create employee details """
    phone_no = serializers.RegexField("^0?[6-9]\d{9}$")
    email_address = serializers.EmailField()

    class Meta:
        model = Employee
        fields = (
            'employee_id', 
            'first_name', 
            'last_name', 
            'address', 
            'phone_no', 
            'email_address', 
            'hostel'
            )
    
    def validate_phone_no(self, value):
        if Employee.objects.filter(phone_no=value).exists():
            raise serializers.ValidationError('Phone number already exists')
        return value


class EmployeeSerializer(serializers.ModelSerializer):
    """ serializer to display or list out employee details """
    phone_no = serializers.RegexField("^0?[6-9]\d{9}$")
    email_address = serializers.EmailField()
    hostel = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = Employee
        fields = (
            'employee_id', 
            'full_name', 
            'address', 
            'phone_no', 
            'email_address', 
            'hostel'
            )


class CreateHostelSerializer(serializers.ModelSerializer):
    phone_no = serializers.RegexField("^0?[6-9]\d{9}$")
    manager_id = serializers.IntegerField()

    class Meta:
        model = Hostel
        fields = (
            'name', 
            'address', 
            'phone_no', 
            'manager_id', 
            'room_limit'
            )
    
    def validate_phone_no(self, value):
        """ validate unique phone number exists """
        if Hostel.objects.filter(phone_no=value).exists():
            raise serializers.ValidationError('Phone number already exists')
        return value
    
    def validate_name(self, value):
        """ hostel name should be unique """
        if Hostel.objects.filter(name=value).exists():
            raise serializers.ValidationError('Hostel name already exists. Please keep some other name')
        return value


class StudentSerializer(serializers.ModelSerializer):
    """ serialize student data """

    class Meta:
        model = Student
        fields = (
            'first_name', 
            'last_name', 
            'address', 
            'phone_no'
            )
    
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
        fields = (
            'student', 
            'room', 
            'check_in_date', 
            'check_out_date'
            )

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
        fields = (
            'booking_id',
            'student',
            'room',
            'roomprice',
            'status',
            'booking_date',
            'check_in_date',
            'check_out_date',
            'no_of_nights'
            )


class CreatePaymentSerializer(serializers.ModelSerializer):
    """ while doing payment serialize payment details """
    
    class Meta:
        model = Payment
        fields = (
            'student', 
            'booking', 
            'payment_mode'
            )

    def validate_booking(self, value):
        """ validate if payment details exist for this booking"""
        if Payment.objects.filter(booking=value).exists():
            raise serializers.ValidationError({
                "error" : "Payment was already done for this booking"
            })
        return value
    
    def validate_student(self, value):
        """ deny payment if already done by student """
        if Payment.objects.filter(student=value).exists():
            raise serializers.ValidationError({
                "error" : "Student have already done payment"
            })
        return value


class PaymentSerializer(serializers.ModelSerializer):
    """ serializers the payment details when displaying """
    student = serializers.SlugRelatedField(read_only=True, slug_field='full_name')
    booking_date = serializers.SlugRelatedField(read_only=True, source='booking', slug_field='booking_date')
    check_in_date = serializers.SlugRelatedField(read_only=True, source='booking', slug_field='check_in_date')
    check_out_date = serializers.SlugRelatedField(read_only=True, source='booking', slug_field='check_out_date')
    payment_datetime = serializers.DateTimeField(read_only=True, format="%Y-%m-%d")
    room = serializers.SerializerMethodField()
    room_price = serializers.ReadOnlyField()
    total_payments = serializers.ReadOnlyField()
    no_of_nights = serializers.ReadOnlyField()
    

    class Meta:
        model = Payment
        fields = (
            'payment_id',
            'student', 
            'booking_date',
            'check_in_date',
            'check_out_date', 
            'room', 
            'room_price',
            'no_of_nights', 
            'payment_mode', 
            'payment_datetime', 
            'total_payments'
            )
    
    def get_room(self, obj):
        """ get room description """
        return obj.booking.room.description

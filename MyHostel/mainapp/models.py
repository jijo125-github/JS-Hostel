from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator

PHONE_NO_REGEX = RegexValidator(r"^0?[6-9]\d{9}$")
ROOM_STATUS_CHOICES = (
        ('reserved', 'Reserved'),
        ('vacant', 'Vacant')
    )

# Create your models here.

class Student(models.Model):
    """ Hostel Student Details """
    student_id  = models.AutoField(primary_key=True)
    first_name  = models.CharField(max_length=50)
    last_name   = models.CharField(max_length=50, blank=True, null=True)
    address     = models.TextField(max_length=50)
    phone_no    = models.CharField(max_length=11, validators=[PHONE_NO_REGEX])

    @property
    def full_name(self):
        if self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.first_name

    def __str__(self):
        return self.full_name


class Hostel(models.Model):
    """ Hostel Branch Details """
    hostel_branch_id   = models.AutoField(primary_key=True)
    name               = models.CharField(max_length=50)
    address            = models.TextField(max_length=100)
    phone_no           = models.CharField(max_length=11, validators=[PHONE_NO_REGEX])
    manager_id         = models.PositiveIntegerField(validators=[MaxValueValidator(99999)])

    def __str__(self):
        return f'Hostel-{self.name}'


class Room(models.Model):
    """ Room Details """
    room_id     = models.AutoField(primary_key=True)
    hostel      = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    description = models.CharField(max_length=50)
    price       = models.PositiveIntegerField()
    status      = models.CharField(max_length=8, choices=ROOM_STATUS_CHOICES)

    def is_room_vacant(self):
        """ if room vacant, return True """
        return self.status == 'vacant'
            
    def __str__(self):
        return f'Room number-{self.room_id}'


class Booking(models.Model):
    """ Booking Details """
    booking_id      = models.AutoField(primary_key=True)
    student         = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='bookings')
    room            = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    booking_date    = models.DateField(auto_now_add=True)
    check_in_date   = models.DateField()
    check_out_date  = models.DateField()
    no_of_nights    = models.PositiveIntegerField(validators=[MaxValueValidator(20)])

    def __str__(self):
        return f'{self.student}-{self.booking_id}'


class Employee(models.Model):
    employee_id     = models.AutoField(primary_key=True)
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50, blank=True, null=True)
    address         = models.TextField(max_length=100)
    phone_no        = models.CharField(max_length=11, validators=[PHONE_NO_REGEX])
    email_address   = models.EmailField(max_length=50)
    hostel          = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='employees')

    @property
    def full_name(self):
        if self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.first_name

    def __str__(self):
        return self.full_name


class Payment(models.Model):
    payment_id  = models.AutoField(primary_key=True)
    student     = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    booking     = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    
    @property
    def room_price(self):
        return self.booking.room.price

    @property
    def no_of_nights(self):
        return self.booking.no_of_nights
    
    def calculate_total_payment(self):
        return round(self.room_price * self.no_of_nights)
    
    @property
    def total_payments(self):
        return self.calculate_total_payment()
    
    def __str__(self):
        return f'{self.student}-{self.payment_id}'


class Transcation(models.Model):
    transaction_id  = models.AutoField(primary_key=True)
    student         = models.ForeignKey(Student, on_delete=models.CASCADE)
    booking         = models.ForeignKey(Booking, on_delete=models.CASCADE)
    payment         = models.ForeignKey(Payment, on_delete=models.CASCADE)
    employee        = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.student}-{self.transaction_id}'
    
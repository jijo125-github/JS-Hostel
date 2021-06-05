from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from .models import Student, Booking, Employee, Room, Hostel

# Create your tests here.

class StudentTestCase(APITestCase):
    """ 
        TestCase to check all student logics
        --> create Student, 
        --> restrict student copies, 
        --> restrict duplicate phone_numbers
    """
    def setUp(self):
        self.student_attrs = {
            "first_name" : "Johns",
            "last_name" : "JS",
            "address" : "Bhavnath-1",
            "phone_no" : "8849091264"
            }
        fname = self.student_attrs['first_name']
        lname = self.student_attrs['last_name']
        addr = self.student_attrs['address']
        phone = self.student_attrs['phone_no']
        Student.objects.create(first_name=fname, last_name=lname, address=addr, phone_no = phone)
        self.currentCount = Student.objects.count()
            
    def test_create_student(self):
        """ test post request to create a student works or not """
        new_student_attr = self.student_attrs.copy()
        new_student_attr['first_name'] = 'Jijo'
        new_student_attr['phone_no'] = '9426481564'
        response = self.client.post('/api/v1/createStudent/', new_student_attr)
        if response.status_code != 201:
            print(response.data)
        self.assertEqual(Student.objects.count(), self.currentCount + 1)

        for key, value in new_student_attr.items():
            self.assertEqual(response.data[key], value)

    def test_duplicate_student_invalid(self):
        """ test if student already exists, new student object not created """
        duplicate_student_attr = self.student_attrs
        response = self.client.post('/api/v1/createStudent/', duplicate_student_attr)
        latest_count = Student.objects.count()
        if response.status_code != 201:
            self.assertTrue(response.data['Failed'])
        self.assertNotEqual(response.status_code, 201)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.currentCount, latest_count)
    
    def test_phoneno_duplicate(self):
        """ test if phone number already exists, it doesn't allow """
        duplicate_student_attr = self.student_attrs.copy()
        duplicate_student_attr.update(first_name='Test', last_name='ABC')
        response = self.client.post('/api/v1/createStudent/', duplicate_student_attr)
        if response.status_code != 201:
            error_message = response.data.get('phone_no').get('error')
            self.assertIn('This phone number already exists', error_message)
            self.assertEqual(response.status_code, 400)
        self.assertEqual(self.currentCount, Student.objects.count())
        

class BookingTestCase(APITestCase):
    """
        TestCase to check all booking logics
    """
    def setUp(self):
        self.booking_attrs = {
            "student": "1",
            "room": "1",
            "check_in_date": "2021-05-19",
            "check_out_date": "2021-05-23"
            }
        Hostel.objects.create(name='Pragati Mens Hostel',
         address='JV Colony, Rajiv gandhi Nagar, Gachibowli, Hyderabad, Telangana 500032',
         phone_no='09922134512',
         manager_id='1',
         room_limit='50'
         )
        tHostel = Hostel.objects.first()
        Room.objects.create(hostel=tHostel, description='King Sized Bedroom', price=3000, status='vacant')
        Student.objects.create(first_name='Test', last_name='123', address='qwerty', phone_no = 9999912345)
        self.current_count = Booking.objects.count()

    def test_create_booking(self):
        response = self.client.post('/api/v1/booking/', self.booking_attrs)
        if response.status_code != 201:
            print('Response data', response.data)
            self.assertRaises(ValidationError)
        self.assertEqual(Booking.objects.count(), self.current_count + 1)
        self.assertEqual(response.data['room_status'], 'Reserved')
        self.assertGreaterEqual(response.data['check_out_date'], response.data['check_in_date'], 
        msg='Check_out_date should be greater than check_in_date')


class HostelTestCase(APITestCase):
    """
        TestCase to check all hostel logics
        --> only unique hostel names allowed
    """
    def setUp(self):
        self.hostel_attrs = {
            "name": "Pragati Mens Hostel",
            "address": "Bhavnath Bangalore",
            "phone_no": "9991231231",
            "manager_id": "1",
            "room_limit" : "40"
            }
        Hostel.objects.create(name='Pragati Mens Hostel',
         address='JV Colony, Rajiv gandhi Nagar, Gachibowli, Hyderabad, Telangana 500032',
         phone_no='09922134512',
         manager_id='1',
         room_limit='50'
         )
        self.currentCount = Hostel.objects.count()
    
    def test_duplicate_fields(self):
        """ test if hostelname already exists, deny creation"""
        response = self.client.post('/api/v1/createHostel/', self.hostel_attrs)
        if response.status_code != 201:
            self.assertRaises(ValidationError)
        self.assertEqual(response.status_code, 400)
        self.assertNotEqual(self.currentCount, self.currentCount + 1)
    
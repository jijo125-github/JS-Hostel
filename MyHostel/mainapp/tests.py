from rest_framework.test import APITestCase
from .models import Student, Booking, Employee, Room, Hostel

# Create your tests here.

class StudentTestCase(APITestCase):
    """ 
        TestCase to check all student logics
        --> create Student, restrict student copies
    """
    def setUp(self):
        self.student_attrs = {
            "first_name" : "Johns",
            "last_name" : "JS",
            "address" : "Bhavnath-1",
            "phone_no" : "8849091164"
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

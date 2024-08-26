from django.test import TestCase
from . models import CustomUser
class libraryAppTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username = 'testuser', password='password123', role = 'user', mobile_number='1234567890', address='address1')
        self.librarian = CustomUser.objects.create(username='testuser2',password='password456', role='librarian', mobile_number='0987654321',address='address2')
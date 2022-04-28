from django.test import TestCase
from .models import Complaint
from django.contrib.auth.models import User

# Create your tests here.

class test_complaints(TestCase):
    def test_complaint(self):
        user = User.objects.create_user(username='testuser', password='12345')

        complaint = Complaint.objects.create(user=user, reason='test',other_reason='test',description='test',state='test')

        complaint.save()

        db_complaint = Complaint.objects.get(id=complaint.id)

        self.assertEqual(db_complaint.user, user)
        self.assertEqual(db_complaint.reason, 'test')
        self.assertEqual(db_complaint.other_reason, 'test')
        self.assertEqual(db_complaint.description, 'test')
        self.assertEqual(db_complaint.state, 'test')


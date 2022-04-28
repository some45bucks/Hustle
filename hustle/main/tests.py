from django.db import transaction
from django.test import TestCase
from .models import User, UserData, CustomerData, WorkerData

# Create your tests here.

class testUser(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username='testuser', password='12345')

        uData = UserData.objects.create(user=user,phone_number='1234567890')
        cData = CustomerData.objects.create(user=user,street='123 Main St',city='Anytown',state='CA',zip_code=12345)
        wData = WorkerData.objects.create(user=user)

        user.save()
        uData.save()
        cData.save()
        wData.save()

        db_user = User.objects.get(username='testuser')

        self.assertEqual(db_user.username, 'testuser')
        self.assertNotEqual(db_user.password, '12345')

        self.assertEqual(db_user.data.phone_number, '1234567890')
        self.assertEqual(db_user.data.money, 0)

        self.assertEqual(db_user.customer_data.street, '123 Main St')
        self.assertEqual(db_user.customer_data.street2, '')
        self.assertEqual(db_user.customer_data.city, 'Anytown')
        self.assertEqual(db_user.customer_data.state, 'CA')
        self.assertEqual(db_user.customer_data.zip_code, '12345')

        self.assertNotEqual(db_user.worker_data, None)

        try:
            with transaction.atomic():
                User.objects.create_user(username='testuser', password='12345')
            self.fail('Should have raised an Error')
        except:
            pass

        User.objects.create_user(username='duplicateName', password='12345')

        db_user.username = 'duplicateName'

        try:
            with transaction.atomic():
                db_user.save()
            self.fail('Should have raised an Error')
        except:
            pass








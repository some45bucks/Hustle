from django.test import TestCase
from .models import Review
from django.contrib.auth.models import User
# Create your tests here.

class test_reviews(TestCase):
    def test_reviews(self):
        user = User.objects.create_user(username='testuser', password='12345')
        review = Review.objects.create(worker=user, rating=5, comments='This is a good worker',create_date='2019-01-01')

        review.save()

        db_review = Review.objects.get(id=review.id)

        self.assertEqual(db_review.worker, user)
        self.assertEqual(db_review.rating, 5)
        self.assertEqual(db_review.comments, 'This is a good worker')



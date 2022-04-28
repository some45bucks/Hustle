from django.db import transaction
from django.test import TestCase
from .models import Job, JobType, Bid
from django.contrib.auth.models import User

# Create your tests here.

class test_jobs(TestCase):
    def test_jobs(self):
        user = User.objects.create(username='testuser')
        job_type = JobType.objects.create(type='test_job_type')

        try:
            with transaction.atomic():
                Job.objects.create(time_estimate=1,
                                   zip_code=12345,
                                   customer= None,
                                   accepted_bid=None,
                                   complete=False,
                                   completion_window_start='2019-01-01',
                                   completion_window_end='2019-01-01',
                                   type=None,
                                   claimed_user=None,
                                   cancelled=False)
            self.fail('Should have raised an Error')
        except:
            pass

        try:
            with transaction.atomic():
                Job.objects.create(time_estimate=1,
                                   zip_code=12345,
                                   customer= user,
                                   accepted_bid=None,
                                   complete=False,
                                   completion_window_start='2019-01-01',
                                   completion_window_end='2019-01-01',
                                   type=None,
                                   claimed_user=None,
                                   cancelled=False)
            self.fail('Should have raised an Error')
        except:
            pass

        job = Job.objects.create(time_estimate=1,
                                 zip_code=12345,
                                 customer= user,
                                 accepted_bid=None,
                                 complete=False,
                                 completion_window_start='2019-01-01',
                                 completion_window_end='2019-01-01',
                                 type=job_type,
                                 claimed_user=None,
                                 cancelled=False)

        job.save()

        db_job = Job.objects.get(id=job.id)

        self.assertEqual(db_job.time_estimate, 1)
        self.assertEqual(db_job.zip_code, '12345')
        self.assertEqual(db_job.customer, user)
        self.assertEqual(db_job.customer.username, 'testuser')
        self.assertEqual(db_job.accepted_bid, None)
        self.assertEqual(db_job.complete, False)
        self.assertEqual(db_job.type, job_type)
        self.assertEqual(db_job.type.type, 'test_job_type')
        self.assertEqual(db_job.claimed_user, None)
        self.assertEqual(db_job.cancelled, False)

        bid = Bid.objects.create(bid=1,user=user,selected_job=job)

        bid.save()

        db_bid = Bid.objects.get(id=bid.id)

        db_job.accepted_bid = db_bid
        db_job.complete = True
        db_job.claimed_user = db_bid.user
        db_job.save()

        self.assertEqual(db_job.accepted_bid, db_bid)
        self.assertEqual(db_job.complete, True)
        self.assertEqual(db_job.accepted_bid.user, db_job.claimed_user)
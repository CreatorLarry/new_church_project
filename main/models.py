import os
import uuid

from django.contrib.auth.views import LoginView
from django.db import models
from django.utils.timezone import now


def generate_unique_name(instance, filename):
    name = uuid.uuid4()  #
    full_file_name = f'{name}-{filename}'
    return os.path.join("profile_pictures", full_file_name)

class MemberLoginView(LoginView):
    template_name = 'login.html'

# Create your models here.
class Member(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    department = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    profile_pic = models.ImageField(upload_to=generate_unique_name, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Member'
        verbose_name_plural = 'Members'
        db_table = 'members'


class Deposit(models.Model):
    amount = models.IntegerField()
    status = models.BooleanField(default=False)
    deposit_for = models.CharField(
        max_length=200,
        choices=[
            ('TITHE', 'Tithe'),
            ('THANKSGIVING', 'Thanksgiving'),
            ('WEDDING', 'Wedding'),
            ('OFFERTORY', 'Offertory'),
            ('FIRST FRUIT', 'First Fruit'),
            ('CHURCH PROJECT', 'Church Project'),
            ('OTHERS', 'Others'),
        ],
        default='OFFERTORY',
    )
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='deposits')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.member.first_name} - {self.amount}"

    class Meta:
        db_table = 'deposits'


class Transaction(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField(default=200)  # Default monthly registration fee
    month = models.DateField(default=now)  # Track the month of payment
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='PENDING')
    merchant_request_id = models.CharField(max_length=100)
    code = models.CharField(max_length=30, null=True)
    checkout_request_id = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.member.first_name} - {self.amount} Ksh ({self.month.strftime("%B %Y")})'

    @staticmethod
    def check_payment_status(member, year, month):
        """
        Check if a member has paid for a given month.
        :param member: Member instance
        :param year: Year to check
        :param month: Month to check
        :return: True if paid, False otherwise
        """
        return Transaction.objects.filter(
            member=member,
            month__year=year,
            month__month=month
        ).exists()

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-month']
        db_table = 'transactions'


class Project(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('upcoming', 'Upcoming'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-start_date']


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    head = models.CharField(max_length=100, blank=True, null=True)  # Department head's name
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['name']

# def __str__(self):
#     return f'{self.merchant_request_id} - {self.code} - {self.amount}'

# run the migrations
# python manage.py makemigrations
# python manage.py migrate

# python manage.py populate

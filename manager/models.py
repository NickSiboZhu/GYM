from django.db import models


class Customer(models.Model):
    Customer_id = models.AutoField(primary_key=True)
    sex = models.CharField(max_length=10)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    ph_num = models.CharField(max_length=20)
    avatar = models.BinaryField()  # Use BinaryField for storing image data as MEDIUMBLOB
    account = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'Customer'  # This is to specify the exact table name in the database


class Manager(models.Model):
    Manager_id = models.AutoField(primary_key=True)
    sex = models.CharField(max_length=10)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    ph_num = models.CharField(max_length=20)
    avatar = models.BinaryField(null=True, blank=True)
    account = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'Manager'  # This is to specify the exact table name in the database
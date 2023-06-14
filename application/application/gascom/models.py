from django.db import models

# Create your models here.
class Staff(models.Model):
    num=models.CharField(max_length=20,primary_key=True)
    name=models.CharField(max_length=20)
    phonenum=models.CharField(max_length=25)
    password=models.CharField(max_length=25)

class Customer(models.Model):
    
    name=models.CharField(max_length=20)
    phonenum=models.CharField(max_length=20,primary_key=True)
    address=models.CharField(max_length=50)
    password=models.CharField(max_length=20)
    money=models.IntegerField(default=0)

class Deliery_staff(models.Model):
    num=models.CharField(max_length=20,primary_key=True)
    name=models.CharField(max_length=20)
    phonenum=models.CharField(max_length=20)
    

class Gas_category(models.Model):
    num=models.CharField(max_length=20,primary_key=True)
    category_name=models.CharField(max_length=20)
    storage=models.IntegerField()
    price=models.IntegerField()
    description=models.CharField(max_length=50,null=True)

class Supplier(models.Model):
    num=models.CharField(max_length=20,primary_key=True)
    name=models.CharField(max_length=20)
    phonenum=models.CharField(max_length=25)
    

class Gas_in(models.Model):
    num=models.CharField(max_length=20,primary_key=True)
    date=models.DateTimeField()
    category_num=models.ForeignKey(Gas_category,on_delete=models.SET_NULL,null=True)
    supplier_num=models.ForeignKey(Supplier,on_delete=models.SET_NULL,null=True)
    amount=models.IntegerField()
    per_price=models.IntegerField()

class Gas_out(models.Model):
    num=models.IntegerField(primary_key=True)
    date=models.DateTimeField()
    category_num=models.ForeignKey(Gas_category,on_delete=models.SET_NULL,null=True)
    customer_pho=models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True)
    amount=models.IntegerField()
    per_price=models.IntegerField()
    is_deliery=models.IntegerField(default=0)

class Deliery_gas(models.Model):
    num=models.IntegerField(primary_key=True)
    deliery_id=models.ForeignKey(Deliery_staff,on_delete=models.SET_NULL,null=True)
    gas_out_id=models.ForeignKey(Gas_out,on_delete=models.SET_NULL,null=True)

    













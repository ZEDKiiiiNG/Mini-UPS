from django.db import models

# Create your models here.
class User(models.Model):
    '''base user class can be driver'''


    name = models.CharField(max_length=128,unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class Truck(models.Model):
    truckId = models.IntegerField(default=-1)
    truckX = models.IntegerField(default=-1)
    truckY = models.IntegerField(default=-1)
    truckStatus = models.CharField(max_length=200, default='', null=True)

class Package(models.Model):
    pkgId = models.BigIntegerField(default=-1, primary_key=True,unique=True)
    whId = models.IntegerField(default=-1)
    whX = models.IntegerField(default=-1)
    whY = models.IntegerField(default=-1)
    destX = models.IntegerField(default=-1)
    destY = models.IntegerField(default=-1)
    user = models.ForeignKey(User, on_delete= models.CASCADE, null= True)
    truck = models.ForeignKey(Truck, on_delete= models.CASCADE, null= True)
    pkgStatus = models.CharField(max_length=200, default='', null=True)


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    productId = models.IntegerField(default=-1)
    productDescrip = models.CharField(max_length=100, default='', null=True)
    productCount = models.IntegerField(default=-1)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True)


import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UPSsite.settings')
import django
django.setup()
import ups.models
from constant import *
from django.core.mail import send_mail
from UPSsite.settings import EMAIL_HOST_USER

def createUser(username, password1, email):
    new_user = ups.models.User.objects.create()
    new_user.name = username
    new_user.password = password1
    new_user.email = email
    new_user.save()


def savePackage(truck_id, truck_req):
    whid = truck_req.wh.id
    whx = truck_req.wh.x
    why = truck_req.wh.y
    user_acc = truck_req.upsaccount
    package_id = truck_req.packageid
    package_status = TRUCK_EN_ROUTE_TO_WAREHOUSE
    # TODO: check
    createPackage(package_id, whid, whx, why, user_acc, truck_id, package_status)
    for product in truck_req.things:
        createProduct(product.id, product.description,product.count, package_id)


def createPackage(pkgId,whId,whX,whY,username,truckId,pkgStatus, destX = -1 ,destY = -1):
    try:
        user = ups.models.User.objects.get(name=username)
    except:
        user = ups.models.User.objects.get(name='default_user')
    truck = ups.models.Truck.objects.get(truckId = truckId)
    new_pkg = ups.models.Package(pkgId= pkgId, whId = whId, whX = whX, whY = whY, destX = destX, destY = destY,
                                 user= user, truck = truck, pkgStatus =pkgStatus)
    new_pkg.save()


def createProduct(productId,productDescrip,productCount,pkgId):
    package = ups.models.Package.objects.get(pkgId=pkgId)
    # new_prod = ups.models.Product.objects.create()
    # new_prod.productId = productId
    # new_prod.productDescrip = productDescrip
    # new_prod.productCount = productCount
    # new_prod.package = package
    new_prod = ups.models.Product(productId = productId, productDescrip = productDescrip, productCount = productCount,
                                  package = package)
    new_prod.save()
def createTruck(truckId,truckX,truckY,truckStatus):
    truck = ups.models.Truck(truckId = truckId,truckX = truckX,truckY = truckY ,truckStatus =truckStatus )
    truck.save()
def getPickupTruck():
    truck_available_list = ups.models.Truck.objects.exclude(truckStatus='traveling').exclude(truckStatus='loading')
    try:
        truck = truck_available_list[0: 1].get()
    except:
        return -1
    else:
        return truck.truckId
def updateTruckstatus(truckId,truckStatus):
    truck = ups.models.Truck.objects.get(truckId = truckId)
    truck.truckStatus = truckStatus
    truck.save()


def updateTruckstatusAndLocation(truckId,truckStatus,truckX, truckY):
    truck = ups.models.Truck.objects.get(truckId = truckId)
    truck.truckStatus = truckStatus
    truck.truckX = truckX
    truck.truckY = truckY
    truck.save()


def updatePackagestatusAccordingTruck(truckId, X, Y):
    truck = ups.models.Truck.objects.get(truckId=truckId)
    packages = ups.models.Package.objects.filter(truck=truck, pkgStatus=TRUCK_EN_ROUTE_TO_WAREHOUSE, whX=X, whY=Y)
    result_list = []
    for package in packages:
        package.pkgStatus = TRUCK_WAITING_FOR_PACKAGE
        package.save()
        result_list.append(package.pkgId)
    return result_list


def updatePackagestatus(pkgId, pkgStatus):
    package = ups.models.Package.objects.get(pkgId=pkgId)
    user_email = package.user
    package.pkgStatus = pkgStatus
    package.save()
    email_list = []
    email_list.append(package.user.email)
    if pkgStatus == DELIVERED:
        send_mail(
            subject='Package delivered',
            message='Your ride has already been confrimed',
            from_email=EMAIL_HOST_USER,
            recipient_list=email_list,
            fail_silently=False
        )
def getDest(pkgId):
    package = ups.models.Package.objects.get(pkgId=pkgId)
    return [package.destX, package.destY]


if __name__ == '__main__':
   # createUser(2,2,"2@2.com")
   # createTruck(1,1,1,"idle")
   # createPackage(1,1,1,1,2,2,2,1,"truck	en	route	to	warehouse")
   # createProduct(1,'pd1',1,1)
   # print("getPickupTruck() : {}" .format(getPickupTruck()))
   # print("updateTruckstatus : {}", updateTruckstatus(1,"traveling"))
   print("updatePackagestatus : {}" .format(updatePackagestatus(2, DELIVERED)))
   # print("getDest() : {}".format(getDest(1)))


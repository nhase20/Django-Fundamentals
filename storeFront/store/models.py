from django.db import models

class Promotion(models.Model):
    desdescription = models.CharField(max_length=255)
    discount = models.FloatField

class Collection(models.Model):
    title = models.CharField(max_length=255)

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    last_update = models.DateTimeField(auto_now=True)
    Collection = models.ForeignKey(Collection,on_delete=models.PROTECT)
    promotions = models.ManyToManyField(Promotion)


class Customer(models.Model):
    MEMBERSHIP_BROZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BROZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_SILVER, 'Gold'),
    ]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    membership = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BROZE)

class Order(models.Model):
    PENDING = 'P'
    COMPLETE = 'C'
    FAILED = 'F'

    PAYMENT_STATUS = [
        (PENDING, 'Pending'),
        (COMPLETE, 'Complete'),
        (FAILED, 'Failed'),
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    payment_status = models.CharField(max_length=1, choices=PAYMENT_STATUS, default=PENDING)
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete= models.PROTECT)
    product = models.ForeignKey(Product, on_delete= models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)



class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=2555)
    # With on_delete= ...CASCADE deleting a customer, the associated address will also be deleted
    # ...SET_NULL when customer is deleted, the child record( the address) will not be deleted, it will stay in the database and customer fiel/column will be set to null (but field doesn't accept null values) therefore do not use
    # ...SET_DEFAULT is used instead
    # PROTECT prevent deletion, if there is a child associated with this parent, parent cannot be deleted, first delete child
    # Primary key is set to create a one-to-one relationship
    # Django identifies the custome as primary key not creating a new one thus making sure each customer has 1 address
    # No need to add address in customer because Django does this automatically
    customer = models.OneToOneField(Customer,on_delete=models.CASCADE,primary_key=True)

    # ...ForeignKey and removing primary key is a one-to-many relationship


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
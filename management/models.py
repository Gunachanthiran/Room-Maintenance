from django.db import models

class AddRoommate(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    number = models.IntegerField()
    city = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    date = models.DateField(auto_now=True)

    class Meta:
        db_table = "AddRoommate"


class AddExpense(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.ForeignKey(AddRoommate, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100)
    item_price = models.FloatField()
    date = models.DateField()

    class Meta:
        db_table = "AddExpense"

class ExpensePaidAmount(models.Model):
    id = models.BigAutoField(primary_key=True)
    month_year = models.CharField(max_length=50)
    name = models.ForeignKey(AddRoommate, on_delete=models.CASCADE)
    no_of_days = models.IntegerField(null=True)
    food_expense = models.FloatField()
    total_paid_pub = models.FloatField(null=True, default=0)
    pub = models.FloatField(null=True, default=0)
    balance = models.FloatField(null=True, default=0)
    purchase = models.FloatField(null=True, default=0)
    
    class Meta:
        db_table = "ExpensePaidAmount"

class PUBBillAmount(models.Model):
    id = models.BigAutoField(primary_key=True)
    pre_date = models.DateField(null=True)
    prev_read = models.FloatField(default=0)
    cur_date = models.DateField(null=True)
    cur_read = models.FloatField(default=0)
    total_units = models.FloatField(default=0)
    refuse_amt = models.FloatField(default=0)
    water_amt = models.FloatField(default=0)
    gst = models.FloatField(default=0)
    total_amt = models.FloatField(null=True, default=0)
    food_date = models.CharField(max_length=50, null=True)
    
    class Meta:
        db_table = "PUBBillAmount"

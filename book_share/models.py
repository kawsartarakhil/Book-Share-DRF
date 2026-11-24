from django.db import models
from accounts.models import CustomUser

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Books(models.Model):
    CONDTITON = (
        ("new","New"),
        ("good","Good"),
        ("average","Averge"),
        ("poor","Poor")
    )
    RATING = (
        ("1","one star"),
        ("2","two star"),
        ("3","three star"),
        ("4","four star"),
        ("5","five star"),
    )
    STATUS = (
    ("available","Available"),
    ("exchanged","Exchanged"),
    )
    title = models.CharField(max_length=150)
    owner = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    author = models.CharField(max_length=100)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name="books")
    condition = models.CharField(choices=CONDTITON)
    city = models.CharField(max_length=100)
    description = models.TextField(null=True,blank=True)
    status = models.CharField(choices=STATUS)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Trade(models.Model):
    STATUS = (
        ("pending","Pending"),
        ("accepted","Accepted"),
        ("rejected","Rejected"),
        ("cancelled","Cancelled")
    )
    sender = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    requested_book = models.ForeignKey(Books,on_delete=models.CASCADE,related_name="requested_trades")
    offered_book = models.ForeignKey(Books,on_delete=models.CASCADE,related_name="offered_trades")
    message = models.TextField()
    status = models.CharField(max_length=20,choices=STATUS)
    traded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.requested_book}"


class Review(models.Model):
    trade = models.ForeignKey(Trade,on_delete=models.CASCADE)
    reviewer = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="reviews_written")
    reviewed_user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="reviews_received")
    rating = models.IntegerField()
    comment = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.rating)
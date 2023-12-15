from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=100)
    authors = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    quantity = models.PositiveIntegerField(default=0)
    publisher = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.title


class Members(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    debt = models.IntegerField(default=0)
    def __str__(self):
        return self.first_name+" "+self.last_name

class Transactions(models.Model):
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    member = models.ForeignKey(Members,on_delete=models.CASCADE)
    issue_date = models.DateField(null=True,blank=True)
    return_date = models.DateField(null=True,blank=True)
    rent_fee = models.IntegerField(default=0)


    def __str__(self):
        return str(self.id)

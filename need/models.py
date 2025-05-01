from django.db import models
from django.contrib.auth.models import User


class PublishManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status="publish")


class Kind(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

class Need(models.Model):
    STATUS_CHOICES = (
        ('first_review','First_Review'),
        ('publish','Publish'),
        ('donor_find','Donor_Find'),
        ('second_review','Second_Review'),
        ('transportation','Transportation'),
        ('complated','Complated'),
        ('cancelled','Cancelled'),
        ('rejected','Rejected')
    )

    name = models.CharField(max_length=40)
    needy = models.ForeignKey(User,on_delete=models.CASCADE,related_name='received_donations')
    donor=models.ForeignKey(User,null=True,on_delete=models.CASCADE,related_name='made_donations')
    kind=models.ForeignKey(Kind,on_delete=models.CASCADE)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='first_review')
    address=models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    note=models.TextField(blank=True)

    objects = models.Manager()
    publish = PublishManager()

    def __str__(self):
        return self.name

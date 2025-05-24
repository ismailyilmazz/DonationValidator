from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid
from django.utils import timezone
from django.utils.text import slugify



class PublishManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status="publish")


class Kind(models.Model):
    name = models.CharField(max_length=40,unique=True)
    slug = models.SlugField(max_length=40,unique=True)
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

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    needy = models.ForeignKey(User,on_delete=models.CASCADE,related_name='received_donations')
    donor=models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE,related_name='made_donations')
    kind=models.ForeignKey(Kind,on_delete=models.CASCADE)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='first_review')
    address=models.CharField(max_length=100,blank=True,null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    note=models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        creating = self.pk is None  
        super().save(*args, **kwargs)
        if creating and not self.slug:
            while True:
                name_part = slugify(self.name)[:6]
                uid_part = str(uuid.uuid4())[:8]  
                self.slug = f"{name_part}{uid_part}"
                if not Need.objects.filter(slug=self.slug).exists():
                    break
            super().save(update_fields=["slug"])

    def get_absolute_url(self):
        return reverse(
            'need:detail_view',
            args=[self.created.year,self.created.month,self.created.day,self.slug]
        )

    def has_pending_offer(self):
        return self.offers.filter(status='pending').exists()

    def get_pending_offer(self):
        return self.offers.filter(status='pending').first()

    objects = models.Manager()
    publish = PublishManager()

    def __str__(self):
        return self.name


class Offer(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    need = models.ForeignKey(Need, on_delete=models.CASCADE, related_name='offers')
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_offers')
    donor_first_name = models.CharField(max_length=50)
    donor_last_name = models.CharField(max_length=50)
    confirmed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    note = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.donor_first_name} {self.donor_last_name} - {self.need.name}"

    class Meta:
        ordering = ['-created']
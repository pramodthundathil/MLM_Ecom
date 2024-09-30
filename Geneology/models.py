from django.db import models
from Home.models import CustomUser


class Franchise_request(models.Model):
    frachise_type = models.CharField(max_length=20)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return 'Franchise Request on {} For {}'.format(self.date, self.frachise_type) 

class FreeSponsership(models.Model):
    name = models.CharField(max_length=100)
    idnumber = models.CharField(max_length=10)
    date = models.DateField(auto_now_add=True)
    
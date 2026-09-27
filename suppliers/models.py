from django.db import models
# Creation de supplier model pour representer les fournisseurs
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name
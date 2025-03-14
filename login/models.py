from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class RegistrarUsuario(AbstractUser):
    cedula = models.CharField(max_length=20, unique=True)  # Unique identifier
    email = models.EmailField(unique=True)
    username = None  # Remove username field since we're using cedula

    # Authentication settings
    USERNAME_FIELD = 'cedula'  
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.cedula})"
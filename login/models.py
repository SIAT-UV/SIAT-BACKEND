from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random
from django.db.models.functions import Lower
# Create your models here.

class Usuario(AbstractUser):
    cedula = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    username = None

    # Campos para OTP
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiration = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'cedula'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    class Meta:
        # Asegura unicidad de email sin distinguir mayúsculas
        constraints = [
            models.UniqueConstraint(
                Lower('email'),
                name='unique_email_ci'
            )
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.cedula})"

    def save(self, *args, **kwargs):
        # Normaliza email
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    def generate_otp(self):
        self.otp = f"{random.randint(100000, 999999):06d}"
        # Expira en 5 minutos, respetando zona horaria
        self.otp_expiration = timezone.now() + timezone.timedelta(minutes=5)
        self.save(update_fields=['otp', 'otp_expiration'])
        return self.otp

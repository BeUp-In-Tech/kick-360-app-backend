import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, access_code=None, email=None, name=None, **extra_fields):
        if not access_code and not email:
            raise ValueError('Either Access Code or Email must be set')
        
        if email:
            email = self.normalize_email(email)
            user = self.model(email=email, name=name, **extra_fields)
        else:
            user = self.model(access_code=access_code, name=name, **extra_fields)
            
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(email=email, name=name, **extra_fields)
        if password:
            user.set_password(password)
        else:
            raise ValueError('Superuser must have a password.')
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    profile_image = models.TextField(null=True, blank=True)
    #profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    position = models.CharField(max_length=50, null=True, blank=True)
    
    # Core login fields
    access_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    
    # Stats
    total_kicks = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    last_session_date = models.DateField(null=True, blank=True)
    
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    @property
    def is_subscription_active(self):
        """Checks if the user has an active, unexpired access code."""
        if self.is_staff:
            return True
        
        # TEMPORARY: Allow any 8-character alphanumeric code for testing
        if self.access_code and len(self.access_code) == 8:
            return True

        from access_codes.models import AccessCode
        active_code = AccessCode.objects.filter(
            user=self, 
            is_consumed=True, 
            expires_at__gt=timezone.now()
        ).exists()
        return active_code

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        indexes = [
            models.Index(fields=['-total_kicks']),
            models.Index(fields=['country']),
            models.Index(fields=['position']),
        ]

    def __str__(self):
        return f"{self.name or 'User'} ({self.access_code})"

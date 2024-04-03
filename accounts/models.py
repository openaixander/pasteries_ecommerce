from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# Create your my custom user models here.

#then creting manager that will handle both normal and admin user

class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email')
        
        if not username:
            raise ValueError('User must have a username')
        
        
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    
    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        
        user.is_admin = True
        user.is_active =True
        user.is_staff = True
        user.is_superadmin = True
        # user.is_superuser = True
        
        user.save(using=self._db)
        return user





# This class here extends from the AbstractBaseUser Model which creates custom user model
class Account(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=50)

    
    objects = MyAccountManager()
    
    # these here are the required fields whenever you need to create a custom user model
    
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_activation_completed = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    
    
    # for one to use the admin site, one will need to submit their email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]
    
    def full_name(self):
        return f"{self.first_name}{self.last_name}" 
    
    def __str__(self) -> str:
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, add_label):
        return True
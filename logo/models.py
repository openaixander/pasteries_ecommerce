from django.db import models
from cloudinary.models import CloudinaryField
# Create your models here.


class CarouselImage(models.Model):
    carousel = CloudinaryField(folder='carousel', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return str(self.carousel)
    

class Weblogo(models.Model):
    web_logo = CloudinaryField(folder='web_logo')
    description = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self) -> str:
            # return f"{self.description[:50]}..."
            return str(self.web_logo)
    
    
class CarouselDescription(models.Model):
    carousel = models.ForeignKey(CarouselImage, on_delete=models.CASCADE)
    header = models.CharField(max_length=50, blank=True, null=True)
    paragraph = models.CharField(max_length=60, blank=True, null=True)
    
    def __str__(self) -> str:
        return str(self.carousel)

class WebPicture(models.Model):
    web_picture = CloudinaryField(folder='web_picture')
    
    def __str__(self) -> str:
        return str(self.web_picture)
    
    
class AboutMe(models.Model):
    web_logo = models.ForeignKey(Weblogo, on_delete=models.CASCADE, null=True)
    description = models.TextField(max_length=700, blank=True)
    work_image = CloudinaryField(folder='logo/my_work')
    
    class Meta:
        verbose_name_plural = 'About Me'
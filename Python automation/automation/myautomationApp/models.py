from django.db import models

# Create your models here.
class MostWanted(models.Model):

    # As string
    name = models.CharField(max_length = 50)
    age = models.CharField(max_length = 10)
    height = models.CharField(max_length = 10)
    weight = models.CharField(max_length = 10)
    
    description = models.TextField(blank = True)
    
    # As url
    image_url = models.URLField(blank = True)
    # time
    created_at = models.DateTimeField( auto_now_add = True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']  # Newest entries first

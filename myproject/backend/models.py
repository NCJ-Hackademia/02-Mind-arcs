from django.db import models



class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    preferences = models.JSONField()
    ocr_language = models.CharField(max_length=10)


class UserPreference(models.Model):

    
    COLOR_TYPES = [
        ('protanopia', 'Protanopia'),
        ('deuteranopia', 'Deuteranopia'),
        ('tritanopia', 'Tritanopia'),
    ]
    type = models.CharField(max_length=20, choices=COLOR_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.type

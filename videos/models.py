from django.db import models
from django.conf import settings
import uuid

class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField(null=True, blank=True) # size in bytes
    duration = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # in seconds
    s3_key = models.CharField(max_length=512, unique=True)
    upload_id = models.CharField(max_length=255, null=True, blank=True)
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

from django.db import models

class Hotspot(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius = models.FloatField()  # Radius in meters
    crash_count = models.IntegerField()
    total_injured = models.IntegerField()
    total_killed = models.IntegerField()
    severity_index = models.FloatField()  # Calculated severity score
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['severity_index']),
            models.Index(fields=['crash_count']),
        ]
    
    def __str__(self):
        return f"Hotspot: {self.name} ({self.crash_count} crashes)"
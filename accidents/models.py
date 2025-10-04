from django.db import models

class Crash(models.Model):
    # Primary key from NYC API
    collision_id = models.BigIntegerField(unique=True, primary_key=True)
    
    # Date and time fields
    crash_date = models.DateTimeField()
    crash_time = models.CharField(max_length=10, blank=True)
    
    # Location fields
    latitude = models.FloatField()
    longitude = models.FloatField()
    borough = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    on_street_name = models.CharField(max_length=200, blank=True)
    cross_street_name = models.CharField(max_length=200, blank=True)
    off_street_name = models.CharField(max_length=200, blank=True)
    
    # Injury/fatality counts
    number_of_persons_injured = models.IntegerField(default=0)
    number_of_persons_killed = models.IntegerField(default=0)
    number_of_pedestrians_injured = models.IntegerField(default=0)
    number_of_pedestrians_killed = models.IntegerField(default=0)
    number_of_cyclist_injured = models.IntegerField(default=0)
    number_of_cyclist_killed = models.IntegerField(default=0)
    number_of_motorist_injured = models.IntegerField(default=0)
    number_of_motorist_killed = models.IntegerField(default=0)
    
    # Contributing factors (up to 5 vehicles)
    contributing_factor_vehicle_1 = models.CharField(max_length=200, blank=True)
    contributing_factor_vehicle_2 = models.CharField(max_length=200, blank=True)
    contributing_factor_vehicle_3 = models.CharField(max_length=200, blank=True)
    contributing_factor_vehicle_4 = models.CharField(max_length=200, blank=True)
    contributing_factor_vehicle_5 = models.CharField(max_length=200, blank=True)
    
    # Vehicle types (up to 5 vehicles)
    vehicle_type_code1 = models.CharField(max_length=50, blank=True)
    vehicle_type_code2 = models.CharField(max_length=50, blank=True)
    vehicle_type_code_3 = models.CharField(max_length=50, blank=True)
    vehicle_type_code_4 = models.CharField(max_length=50, blank=True)
    vehicle_type_code_5 = models.CharField(max_length=50, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['crash_date']),
            models.Index(fields=['borough']),
            models.Index(fields=['latitude', 'longitude']),
        ]
        ordering = ['-crash_date']
    
    def __str__(self):
        return f"Crash {self.collision_id} on {self.crash_date} in {self.borough}"
    
    @property
    def total_severity(self):
        """Calculate total severity score (injuries + 10*fatalities)"""
        return self.number_of_persons_injured + (self.number_of_persons_killed * 10)
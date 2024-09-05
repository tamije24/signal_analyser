from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, FileExtensionValidator


# import datetime

class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=50)
    afa_case_id = models.CharField(max_length=10)
    line_name = models.CharField(max_length=20)
    favorite = models.BooleanField(default=False)
    no_of_terminals = models.PositiveSmallIntegerField(
        default=2, 
        validators=[MinValueValidator(2)])
    created_on = models.DateTimeField(auto_now_add=True)
    last_accessed_on = models.DateTimeField(auto_now=True)
    notes = models.TextField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
      
    class Meta:
        indexes = [
            models.Index(fields=['line_name'])
        ]
        
        ordering = ['created_on']
        
    def __str__(self) -> str:
        return self.project_name
    
    
class File(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, 
                                         related_name='files')
    file_id = models.AutoField(primary_key=True)
    
    cfg_file = models.FileField(
        upload_to='comtrade/files',
        validators=[FileExtensionValidator(allowed_extensions=['cfg'])])
    
    dat_file = models.FileField(
        upload_to='comtrade/files',
        validators=[FileExtensionValidator(allowed_extensions=['dat'])])
    
    station_name = models.CharField(max_length=20, null=True)
    analog_channel_count = models.PositiveSmallIntegerField(null=True)
    digital_channel_count = models.PositiveSmallIntegerField(null=True)
    start_time_stamp = models.DateTimeField(null=True)
    trigger_time_stamp = models.DateTimeField(null=True)
    line_frequency = models.PositiveSmallIntegerField(null=True)
    sampling_frequency = models.PositiveSmallIntegerField(null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['station_name'])
        ]
        # unique_together = [['project', 'cfg_file_name']]
    
class AnalogChannel(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE,  related_name='analog_channels')     
    channel_id = models.CharField(max_length=10, primary_key=True)
    id = models.IntegerField()
    channel_name = models.CharField(max_length=10, default="")
    phase = models.CharField(max_length=5)
    unit = models.CharField(max_length=5)
    primary = models.PositiveSmallIntegerField()
    secondary = models.PositiveSmallIntegerField()
    pors = models.CharField(max_length=1)
    selected = models.BooleanField(default=False)
    
class DigitalChannel(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE,  related_name='digital_channels')     
    channel_id = models.CharField(max_length=10, primary_key=True)
    id = models.IntegerField()
    channel_name = models.CharField(max_length=50, default="")
    normal_state = models.PositiveSmallIntegerField()
    selected = models.BooleanField(default=False)
    

    
   
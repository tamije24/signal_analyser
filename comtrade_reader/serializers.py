
from django.conf import settings
from django.db import transaction
import numpy as np
from rest_framework import serializers
from datetime import datetime

from .models import Project, File , AnalogChannel, DigitalChannel
from core.models import User
from core.serializers import SimpleUserSerializer

from utilities.handle_comtrade import ReadComtrade

class SimpleFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['file_id', 'cfg_file', 'dat_file', 'station_name']
    
class FileSerializer(serializers.ModelSerializer):  
    class Meta:
        model = File
        fields = ['file_id', 'cfg_file', 'dat_file', 'station_name', 'analog_channel_count', 'digital_channel_count', 'start_time_stamp', 'trigger_time_stamp', 'line_frequency', 'sampling_frequency']
       
class CreateFileSerializer(serializers.ModelSerializer):  
    class Meta:
        model = File
        fields = ['file_id', 'cfg_file', 'dat_file']
    
    def create(self, validated_data):       
        with transaction.atomic(): 
            # SAVE FILES
            cfg_file = str(validated_data['cfg_file'])
            dat_file = str(validated_data['dat_file'])
            print(cfg_file)
            file = File(**validated_data)
            file.project_id = self.context['project_id']
            file.save()
            
            cfg_file = settings.MEDIA_ROOT + "/" + str(file.cfg_file)
            dat_file = settings.MEDIA_ROOT + "/" + str(file.dat_file)
            comtrade = ReadComtrade(cfg_file=cfg_file, 
                                    dat_file=dat_file)
            [file_info, an_channels, dig_channels] = comtrade.read_comtrade_config_data()
            
            file.station_name = file_info["station_name"]
            file.analog_channel_count = file_info["analog_channel_count"]
            file.digital_channel_count = file_info["digital_channel_count"]
            file.start_time_stamp = file_info ["start_time_stamp"]
            file.trigger_time_stamp=file_info["trigger_time_stamp"]
            file.line_frequency=file_info["line_frequency"]
            file.sampling_frequency=file_info["sampling_frequency"]
            file.save()    
                                           
            # READ AND SAVE ANALOG CHANNEL INFORMATION          
            analog_channels = [
                AnalogChannel(
                    channel_id = "{}-{}".format(file.file_id, channel["channel_id"]),
                    file_id = file.file_id,
                    id = channel["channel_id"],
                    channel_name = channel["channel_name"],
                    phase = channel["phase"],
                    unit = channel["unit"],
                    primary = channel["primary"],
                    secondary = channel["secondary"],
                    pors = channel["pors"],
                ) for channel in an_channels
            ]           
            AnalogChannel.objects.bulk_create(analog_channels)
                 
            # READ AND SAVE DIGITAL CHANNEL INFORMATION           
            digital_channels = [
                DigitalChannel(
                    channel_id = "{}-{}".format(file.file_id, channel["channel_id"]),
                    file_id = file.file_id,
                    id = channel["channel_id"],
                    channel_name = channel["channel_name"],
                    normal_state = channel["normal_state"]
                ) for channel in dig_channels
            ]                
            DigitalChannel.objects.bulk_create(digital_channels)       
            
            return file
       
#TODO this class must be updated       
class CreateProjectWithFilesSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(read_only=True)
    afa_case_id = serializers.CharField(max_length=10)
    line_name = serializers.CharField(max_length=20)
    no_of_terminals = serializers.IntegerField(min_value=2, default=2)
    files = SimpleFileSerializer(many=True, read_only=True)
    
    def save(self, **kwargs):      
        with transaction.atomic(): 
            # SAVE PROJECT     
            project = Project(**self.validated_data)
            # make project name
            project.project_name = project.line_name + " " + str(datetime.now())  
            # get project user
            project.user = User.objects.get(id=self.context['user_id'])
            # save project
            project.save()       
            
            # SAVE FILES
            cfg_file1 = "./files/KAWA-PAKA1.CFG"
            dat_file1 = "./files/KAWA-PAKA1.DAT"
            cfg_file2 = "./files/PAKA-KAWA1.CFG"
            dat_file2 = "./files/PAKA-KAWA1.DAT"
            comtrade = ReadComtrade(cfg_file1=cfg_file1, 
                                    dat_file1=dat_file1, 
                                    cfg_file2=cfg_file2, 
                                    dat_file2=dat_file2)
            file_info = comtrade.read_comtrade()
            
            files = [
                File(
                    project_id = project.project_id,
                    cfg_file_name=file["cfg_file_name"],
                    file_location=file["file_location"],
                    station_name=file["station_name"],
                    analog_channel_count=file["analog_channel_count"],
                    digital_channel_count=file["digital_channel_count"],
                    start_time_stamp=file["start_time_stamp"],
                    trigger_time_stamp=file["trigger_time_stamp"],
                    line_frequency=file["line_frequency"],
                    sampling_frequency=file["sampling_frequency"]
                ) for file in file_info
            ]
            
            File.objects.bulk_create(files)
                
            return project
     
class ProjectSerializer(serializers.ModelSerializer):
    
    project_name = serializers.CharField(read_only=True)   
    user = SimpleUserSerializer(read_only=True)
    files = SimpleFileSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = ['project_id', 'project_name', 'afa_case_id', 'line_name', 'favorite', 'no_of_terminals', 'notes', 'user', 'files']
        
    def create(self, validated_data):
        project = Project(**validated_data)
        project.project_name = project.line_name + " " + str(datetime.now())  
        project.user = User.objects.get(id=self.context['user_id'])
        
        project.save()
        return project

class ProjectUpdateSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['project_id', 'afa_case_id', 'line_name', 'no_of_terminals', 'favorite','notes']     
      
class AnalogChannelSerializer(serializers.ModelSerializer):
    channel_id = serializers.CharField(read_only=True)  
    id = serializers.IntegerField(read_only=True)
    channel_name = serializers.CharField(read_only=True)  
    phase = serializers.CharField(read_only=True)  
    unit = serializers.CharField(read_only=True)  
    primary = serializers.IntegerField(read_only=True)
    secondary = serializers.IntegerField(read_only=True)
    pors = serializers.CharField(read_only=True)
    
    class Meta:
        model = AnalogChannel
        fields = ['channel_id', 'id', 'channel_name', 'phase', 'unit', 'primary', 'secondary', 'pors', 'selected']     
         
class DigitalChannelSerializer(serializers.ModelSerializer):
    channel_id = serializers.CharField(read_only=True)  
    id = serializers.IntegerField(read_only=True)
    channel_name = serializers.CharField(read_only=True)  
    normal_state = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = DigitalChannel
        fields = ['channel_id', 'id', 'channel_name', 'normal_state', 'selected']    


    
    
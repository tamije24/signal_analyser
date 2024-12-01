
from django.conf import settings
from django.db import transaction
import numpy as np
from rest_framework import serializers
from datetime import datetime, timedelta

from .models import AnalogSignal, DigitalSignal, Project, File , AnalogChannel, DigitalChannel
from core.models import User
from core.serializers import SimpleUserSerializer

from utilities.handle_comtrade import ReadComtrade

class SimpleFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['file_id', 'station_name', 'sampling_frequency', 'start_time_stamp', 'trigger_time_stamp', 'ia_channel', 'ib_channel', 'ic_channel', 'va_channel', 'vb_channel', 'vc_channel', 'd1_channel', 'd2_channel', 'd3_channel', 'd4_channel']
    
class FileSerializer(serializers.ModelSerializer):  
    class Meta:
        model = File
        fields = ['file_id', 'cfg_file', 'dat_file', 'station_name', 'analog_channel_count', 'digital_channel_count', 'start_time_stamp', 'trigger_time_stamp', 'line_frequency', 'sampling_frequency', 'ia_channel', 'ib_channel', 'ic_channel', 'va_channel', 'vb_channel', 'vc_channel', 'd1_channel', 'd2_channel', 'd3_channel', 'd4_channel']
       
class CreateFileSerializer(serializers.ModelSerializer):  
    class Meta:
        model = File
        fields = ['file_id', 'cfg_file', 'dat_file', 'ia_channel', 'ib_channel', 'ic_channel', 'va_channel', 'vb_channel', 'vc_channel', 'd1_channel', 'd2_channel', 'd3_channel', 'd4_channel']
    
    def create(self, validated_data):       
        with transaction.atomic(): 
            # SAVE FILES
            cfg_file = str(validated_data['cfg_file'])
            dat_file = str(validated_data['dat_file'])      
            file = File(**validated_data)
            file.project_id = self.context['project_id']
            file.save()
            # print("File saved")
            
            cfg_file = settings.MEDIA_ROOT + "/" + str(file.cfg_file)
            dat_file = settings.MEDIA_ROOT + "/" + str(file.dat_file)
            
            # READ COMTRADE FILE
            comtrade = ReadComtrade(cfg_file=cfg_file, 
                                    dat_file=dat_file)
            # GET CHANNEL INFORMATION
            [file_info, an_channels, dig_channels] = comtrade.read_comtrade_config_data()
            
            # GET ANALOG SIGNALS
            [total_samples, time_values, an_signals] = comtrade.read_comtrade_analog_signals()
           
            # GET DIGITAL SIGNALS
            [total_samples, time_signal, dig_signals] = comtrade.read_comtrade_digital_signals()
            
            file.station_name = file_info["station_name"]
            file.analog_channel_count = file_info["analog_channel_count"]
            file.digital_channel_count = file_info["digital_channel_count"]
            file.start_time_stamp = datetime.fromisoformat(str(file_info ["start_time_stamp"]))
            file.trigger_time_stamp=datetime.fromisoformat(str(file_info["trigger_time_stamp"]))
            file.line_frequency=file_info["line_frequency"]
            file.sampling_frequency=(1/(time_values[1]-time_values[0]))
            # file.sampling_frequency=file_info["sampling_frequency"]
            file.save()    
            
            time_values
            
            # print("File updated")                        
                                           
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
                ) for channel in an_channels if channel["channel_name"] in [file.ia_channel, file.ib_channel, file.ic_channel, file.va_channel, file.vb_channel, file.vc_channel]
            ]           
            AnalogChannel.objects.bulk_create(analog_channels)
                 
            # print("analog channels saved")         
                 
            # READ AND SAVE DIGITAL CHANNEL INFORMATION             
            digital_channels = [
                DigitalChannel(
                    channel_id = "{}-{}".format(file.file_id, channel["channel_id"]),
                    file_id = file.file_id,
                    id = channel["channel_id"],
                    channel_name = channel["channel_name"],
                    normal_state = channel["normal_state"]
                ) for channel in dig_channels if channel["channel_name"] in [file.d1_channel, file.d2_channel, file.d3_channel, file.d4_channel]
            ]                
            DigitalChannel.objects.bulk_create(digital_channels)       
            
            # print("digital channels saved")    
              
            # STORE THE ANALOG SIGNALS
            analog_samples = []
            ia_channel = list(AnalogChannel.objects.filter(file_id=file.file_id, channel_name=file.ia_channel))
            ib_channel = list(AnalogChannel.objects.filter(file_id=file.file_id, channel_name=file.ib_channel))
            ic_channel = list(AnalogChannel.objects.filter(file_id=file.file_id, channel_name=file.ic_channel)) 
            va_channel = list(AnalogChannel.objects.filter(file_id=file.file_id, channel_name=file.va_channel)) 
            vb_channel = list(AnalogChannel.objects.filter(file_id=file.file_id, channel_name=file.vb_channel)) 
            vc_channel = list(AnalogChannel.objects.filter(file_id=file.file_id, channel_name=file.vc_channel)) 
            
            st_time = datetime.fromisoformat(str(file_info ["start_time_stamp"]))
            tr_time = datetime.fromisoformat(str(file_info["trigger_time_stamp"]))            
            pre_fault = tr_time - st_time
            
            pre_fault_seconds = pre_fault.total_seconds()
            newtime_list = [t for t in time_values if t >= pre_fault_seconds]
            if len(newtime_list) == 0:
                pre_fault_updated = 0
            else:
                pre_fault_updated = newtime_list[0]
                
            # print(st_time, tr_time, pre_fault)
            # print(pre_fault_seconds)
            # print(pre_fault_updated)
             
            for i in range(total_samples):
                t = time_values[i]
                delta = timedelta(microseconds=t*1000000)
                
                analog_samples.append(AnalogSignal(
                    sample_id = "{}-{}".format(file.file_id, i),
                    file_id = file.file_id,
                    time_signal = t - pre_fault_updated,
                    ia_signal = an_signals[ia_channel[0].id-1][i] if len(ia_channel) > 0 else 0,
                    ib_signal = an_signals[ib_channel[0].id-1][i] if len(ib_channel) > 0 else 0,
                    ic_signal = an_signals[ic_channel[0].id-1][i] if len(ic_channel) > 0 else 0,
                    va_signal = an_signals[va_channel[0].id-1][i] if len(va_channel) > 0 else 0,
                    vb_signal = an_signals[vb_channel[0].id-1][i] if len(vb_channel) > 0 else 0,
                    vc_signal = an_signals[vc_channel[0].id-1][i] if len(vc_channel) > 0 else 0,
                    time_stamp = (st_time + delta).strftime('%d/%m/%Y, %H:%M:%S.%f'),
                )) 
                
            AnalogSignal.objects.bulk_create(analog_samples)

            # STORE THE DIGITAL SIGNALS
            digital_samples = []
            d1_channel = list(DigitalChannel.objects.filter(file_id=file.file_id, channel_name=file.d1_channel))
            d2_channel = list(DigitalChannel.objects.filter(file_id=file.file_id, channel_name=file.d2_channel))
            d3_channel = list(DigitalChannel.objects.filter(file_id=file.file_id, channel_name=file.d3_channel))
            d4_channel = list(DigitalChannel.objects.filter(file_id=file.file_id, channel_name=file.d4_channel))
            for i in range(total_samples):
                t = time_values[i]
                digital_samples.append(DigitalSignal(
                    sample_id = "{}-{}".format(file.file_id, i),
                    file_id = file.file_id,
                    time_signal = t,
                    d1_signal = dig_signals[d1_channel[0].id-1][i] if len(d1_channel) > 0 else 0,
                    d2_signal = dig_signals[d2_channel[0].id-1][i] if len(d2_channel) > 0 else 0,
                    d3_signal = dig_signals[d3_channel[0].id-1][i] if len(d3_channel) > 0 else 0,
                    d4_signal = dig_signals[d4_channel[0].id-1][i] if len(d4_channel) > 0 else 0,
                )) 
            DigitalSignal.objects.bulk_create(digital_samples)
            
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
         with transaction.atomic(): 
            # Get all projects of this user
            id=self.context['user_id']
            projects_list = list(Project.objects.select_related('user').filter(user=id).order_by('project_id'))
            
             # delete all projects except the last added one
            for i in range(len(projects_list)-1):
                projects_list[i].delete()
            
            # save current project
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
    primary = serializers.FloatField(read_only=True)
    secondary = serializers.FloatField(read_only=True)
    pors = serializers.CharField(read_only=True)
    
    class Meta:
        model = AnalogChannel
        fields = ['file', 'channel_id', 'id', 'channel_name', 'phase', 'unit', 'primary', 'secondary', 'pors', 'selected']     
         
class DigitalChannelSerializer(serializers.ModelSerializer):
    channel_id = serializers.CharField(read_only=True)  
    id = serializers.IntegerField(read_only=True)
    channel_name = serializers.CharField(read_only=True)  
    normal_state = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = DigitalChannel
        fields = ['file', 'channel_id', 'id', 'channel_name', 'normal_state', 'selected']    

class AnalogSignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalogSignal
        fields =['time_signal', 'ia_signal', 'ib_signal', 'ic_signal', 'va_signal', 'vb_signal', 'vc_signal', 'time_stamp']
        
class DigitalSignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalSignal
        fields =['time_signal', 'd1_signal', 'd2_signal', 'd3_signal', 'd4_signal', 'file']
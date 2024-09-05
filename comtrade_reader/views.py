from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, F
from django.db.models.aggregates import Count
from django.http import HttpResponse
import numpy as np
import json

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly, IsAdminUser, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Project, File, AnalogChannel, DigitalChannel
from .serializers import ProjectSerializer, CreateProjectWithFilesSerializer, FileSerializer, CreateFileSerializer, AnalogChannelSerializer, DigitalChannelSerializer, ProjectUpdateSerialiser

from utilities.handle_comtrade import ReadComtrade
from utilities.dft_phasors import DFTPhasors
from utilities.sequence import Sequence

# This viewset is for viewing and adding projects and related files at one go
class ProjectAndFilesViewSet(ModelViewSet):
    
    http_method_names = ['get', 'post']   
    permission_classes = [IsAuthenticated]
    
    # permission_classes = [DjangoModelPermissions]
    # filter_backends = [SearchFilter, OrderingFilter]
    # search_fields = ['afa_case_id', 'line_name']
    # ordering_fields = ['afa_case_id', 'line_name', 'created_on']
        
    def create(self, request, *args, **kwargs):
        serializer = ProjectSerializer(
            data=request.data,
            context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        # if user.is_staff:
        #     return Project.objects.all()      
        return Project.objects.filter(user=user.id)

    def get_serializer_class(self):
        return ProjectSerializer
 
# this is for viewing and adding a project (no files)
# TODO Logic to delete related files to be implemented
class ProjectViewSet(ModelViewSet):
    
    permission_classes = [IsAuthenticated]
    
    # permission_classes = [DjangoModelPermissions]
    # filter_backends = [SearchFilter, OrderingFilter]
    # search_fields = ['afa_case_id', 'line_name']
    # ordering_fields = ['afa_case_id', 'line_name', 'created_on']
    
    def create(self, request, *args, **kwargs):
        serializer = ProjectSerializer(
            data=request.data,
            context={'user_id': self.request.user.id}
            )
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        # serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Project.objects.select_related('user').prefetch_related('files').all()      
        return Project.objects.select_related('user').filter(user=user.id)

    def get_serializer_class(self):
        if self.request.method == "PUT" or self.request.method == "PATCH":
            return ProjectUpdateSerialiser
        return ProjectSerializer

    # def get_serializer_context(self):
    #     return {'user_id': self.request.user.id}

# TODO Logic to delete related files to be implemented    
class FileViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = CreateFileSerializer(
            data=request.data,
            context={'project_id': self.kwargs['project_pk']}
            )
        serializer.is_valid(raise_exception=True)
        file = serializer.save()
        serializer = FileSerializer(file)
        return Response(serializer.data)
    
    def get_queryset(self):
        return File.objects.filter(project_id=self.kwargs['project_pk'])

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateFileSerializer
        return FileSerializer
    
class AllFilesViewSet(ModelViewSet):
    http_method_names = ['head', 'options']
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]
        
class AnalogChannelViewSet(ModelViewSet):
    http_method_names = ['get', 'patch', 'head', 'options']
    serializer_class = AnalogChannelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AnalogChannel.objects.filter(file_id=self.kwargs['file_pk'])

    def get_serializer_context(self):
        return {'file_id': self.kwargs['file_pk']}

class DigitalChannelViewSet(ModelViewSet):
    http_method_names = ['get', 'patch', 'head', 'options']
    serializer_class = DigitalChannelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DigitalChannel.objects.filter(file_id=self.kwargs['file_pk'])

    def get_serializer_context(self):
        return {'file_id': self.kwargs['file_pk']}
     
class AnalogSignalView(APIView):
    http_method_names = ['get', 'head', 'options']
    # renderer_classes = [JSONRenderer]
    
    def get(self, request, id):    
        
        analog_channel_list = list(AnalogChannel.objects.filter(file_id=id, selected=True))          
        selectedChannels = [anChannel.id for anChannel in analog_channel_list]
        
        file_list = list(File.objects.filter(file_id=id))    
        file = file_list[0]
        
        cfg_file = settings.MEDIA_ROOT + "/" + str(file.cfg_file)
        dat_file = settings.MEDIA_ROOT + "/" + str(file.dat_file)
        comtrade = ReadComtrade(cfg_file=cfg_file, dat_file=dat_file)
        [total_samples, time_signal, an_signals] = comtrade.read_comtrade_analog_signals()
        
        signals = []
        for i in range(total_samples):
            signal = {"time": time_signal[i]}
            for j in range(len(selectedChannels)):
                ch_name = [an_channel.channel_name for an_channel in analog_channel_list if an_channel.id == selectedChannels[j]][0] 
                signal[ch_name] = an_signals[j][i]
         
            signals.append(signal)
            
        analog_signals = {"signals": signals}
        # print(analog_signals)    
        return Response(json.dumps(analog_signals))
        # return Response(analog_signals)
        
class DigitalSignalView(APIView):
    http_method_names = ['get', 'head', 'options']
    # renderer_classes = [JSONRenderer]
    
    def get(self, request, id):    
        
        digital_channel_list = list(DigitalChannel.objects.filter(file_id=id, selected=True))          
        selectedChannels = [digChannel.id for digChannel in digital_channel_list]
        
        file_list = list(File.objects.filter(file_id=id))    
        file = file_list[0]
        
        cfg_file = settings.MEDIA_ROOT + "/" + str(file.cfg_file)
        dat_file = settings.MEDIA_ROOT + "/" + str(file.dat_file)
        comtrade = ReadComtrade(cfg_file=cfg_file, dat_file=dat_file)
        [total_samples, time_signal, dig_signals] = comtrade.read_comtrade_digital_signals()
                          
        signals = []
        for i in range(total_samples):
            signal = {"time":time_signal[i]}
            for j in range(len(selectedChannels)):
                ch_name = [dig_channel.channel_name for dig_channel in digital_channel_list if dig_channel.id == selectedChannels[j]][0] 
                signal[ch_name] = dig_signals[j][i]
 
            signals.append(signal) 
            
        digital_signals = {"signals": signals} 
        return Response(json.dumps(digital_signals))

class PhasorView(APIView):
    http_method_names = ['get', 'head', 'options']
    # renderer_classes = [JSONRenderer]
    
    def get(self, request, id):    
        analog_channel_list = list(AnalogChannel.objects.filter(file_id=id, selected=True))          
        selectedChannels = [anChannel.id for anChannel in analog_channel_list]
        
        file_list = list(File.objects.filter(file_id=id))    
        file = file_list[0]
        
        cfg_file = settings.MEDIA_ROOT + "/" + str(file.cfg_file)
        dat_file = settings.MEDIA_ROOT + "/" + str(file.dat_file)
        comtrade = ReadComtrade(cfg_file=cfg_file, dat_file=dat_file)
        [total_samples, time_signal, an_signals] = comtrade.read_comtrade_analog_signals()
        
        phasors = []
        dftphasor = DFTPhasors(fs=file.sampling_frequency, fn=file.line_frequency)
        for i in range(len(selectedChannels)):
            phasors.append(
                 dftphasor.estimate_dft_phasors(an_signals[selectedChannels[i]-1][:])
            )
        
        split_phasors = []
        for i in range(total_samples):
            split_phasor = {}
            for j in range(len(selectedChannels)):
                ch_name = [an_channel.channel_name for an_channel in analog_channel_list if an_channel.id == selectedChannels[j]][0] 
                split_phasor[ch_name+"-mag"] = np.absolute(phasors[j][i])
                split_phasor[ch_name+"-ang"] = np.angle(phasors[j][i])
         
            split_phasors.append(split_phasor)

        # phasors = np.stack((np.absolute(ia_phasor), np.angle(ia_phasor),
        #                     np.absolute(ib_phasor), np.angle(ib_phasor),
        #                     np.absolute(ic_phasor), np.angle(ic_phasor),
        #                     np.absolute(va_phasor), np.angle(va_phasor),
        #                     np.absolute(vb_phasor), np.angle(vb_phasor),
        #                     np.absolute(vc_phasor), np.angle(vc_phasor),
        #                     np.absolute(i0_phasor), np.angle(i0_phasor),
        #                     np.absolute(i1_phasor), np.angle(i1_phasor),
        #                     np.absolute(i2_phasor), np.angle(i2_phasor),
        #                     np.absolute(v0_phasor), np.angle(v0_phasor),
        #                     np.absolute(v1_phasor), np.angle(v1_phasor),
        #                     np.absolute(v2_phasor), np.angle(v2_phasor),), axis=1)
        
        selected_phasors = {"phasors": split_phasors} 
        return Response(json.dumps(selected_phasors))





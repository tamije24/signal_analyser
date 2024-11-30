from django.conf import settings
from django.db.models.aggregates import Count
import numpy as np
import json
# import logging

# from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly, IsAdminUser, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import AnalogSignal, DigitalSignal, Project, File, AnalogChannel, DigitalChannel
from .serializers import DigitalSignalSerializer, ProjectSerializer, CreateProjectWithFilesSerializer, FileSerializer, CreateFileSerializer, AnalogChannelSerializer, DigitalChannelSerializer, ProjectUpdateSerialiser, AnalogSignalSerializer

from utilities.handle_comtrade import ReadComtrade
from utilities.dft_phasors import DFTPhasors
from utilities.harmonics import Harmonics

# logger = logging.getLogger(__name__)

# TODO: View needs update - This viewset is for viewing and adding projects and related files at one go
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
        
        #TODO: First delete all projects except the last one
        
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
            return Project.objects.select_related('user').prefetch_related('files').all().order_by('project_id')
        # .reverse()     
        return Project.objects.select_related('user').filter(user=user.id).order_by('project_id').reverse()

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
     
class AnalogSignalViewSet(ModelViewSet):
    
    http_method_names = ['get', 'head', 'options']
    serializer_class = AnalogSignalSerializer
    
    def get_queryset(self):
        return AnalogSignal.objects.filter(file_id=self.kwargs['file_pk']).order_by('time_signal')

class DigtialSignalViewSet(ModelViewSet):
    
    http_method_names = ['get', 'head', 'options']
    serializer_class = DigitalSignalSerializer
    
    def get_queryset(self):
        return DigitalSignal.objects.filter(file_id=self.kwargs['file_pk']).order_by('time_signal')
            
class PhasorView(APIView):
    http_method_names = ['get', 'head', 'options']
    # renderer_classes = [JSONRenderer]
    
    def get(self, request, id):    
        file_list = list(File.objects.filter(file_id=id))    
        file = file_list[0]
        
        analog_signals = list(AnalogSignal.objects.filter(file_id=id).order_by('time_signal'))
        ia_signal = [item.ia_signal for item in analog_signals]
        ib_signal = [item.ib_signal for item in analog_signals]
        ic_signal = [item.ic_signal for item in analog_signals]
        va_signal = [item.va_signal for item in analog_signals]
        vb_signal = [item.vb_signal for item in analog_signals]
        vc_signal = [item.vc_signal for item in analog_signals]
        
        phasors = []
        dftphasor = DFTPhasors(fs=file.sampling_frequency, fn=file.line_frequency)
        
        phasors.append(dftphasor.estimate_dft_phasors(ia_signal))
        phasors.append(dftphasor.estimate_dft_phasors(ib_signal))
        phasors.append(dftphasor.estimate_dft_phasors(ic_signal))
        phasors.append(dftphasor.estimate_dft_phasors(va_signal))
        phasors.append(dftphasor.estimate_dft_phasors(vb_signal))
        phasors.append(dftphasor.estimate_dft_phasors(vc_signal))
        
        total_samples = len(ia_signal)
        split_phasors = []
        for i in range(total_samples):
            split_phasor = {}
            split_phasor["ia-mag"] = np.absolute(phasors[0][i])
            split_phasor["ia-ang"] = np.angle(phasors[0][i])
            split_phasor["ib-mag"] = np.absolute(phasors[1][i])
            split_phasor["ib-ang"] = np.angle(phasors[1][i])
            split_phasor["ic-mag"] = np.absolute(phasors[2][i])
            split_phasor["ic-ang"] = np.angle(phasors[2][i])
            split_phasor["va-mag"] = np.absolute(phasors[3][i])
            split_phasor["va-ang"] = np.angle(phasors[3][i])
            split_phasor["vb-mag"] = np.absolute(phasors[4][i])
            split_phasor["vb-ang"] = np.angle(phasors[4][i])
            split_phasor["vc-mag"] = np.absolute(phasors[5][i])
            split_phasor["vc-ang"] = np.angle(phasors[5][i])
         
            split_phasors.append(split_phasor)

        selected_phasors = {"phasors": split_phasors} 
        return Response(json.dumps(selected_phasors))
    
class HarmonicsView(APIView):
    http_method_names = ['get', 'head', 'options']
    # renderer_classes = [JSONRenderer]
    
    def get(self, request, id, start, end):    
        file_list = list(File.objects.filter(file_id=id))    
        file = file_list[0]
        
        analog_signals = list(AnalogSignal.objects.filter(file_id=id).order_by('time_signal'))
        ia_signal = [item.ia_signal for item in analog_signals]
        ib_signal = [item.ib_signal for item in analog_signals]
        ic_signal = [item.ic_signal for item in analog_signals]
        va_signal = [item.va_signal for item in analog_signals]
        vb_signal = [item.vb_signal for item in analog_signals]
        vc_signal = [item.vc_signal for item in analog_signals]
        
        N = end - start                         # Selected window size (no of samples) 
        fs = file.sampling_frequency            # Sampling frequency (Hz)
        fn = file.line_frequency                # Nominal frequency (Hz) 
        Nc = fs/fn                              # Samples / cycle
        Nw = N / Nc                             # No of cycles of data available
        new_end = start + int(np.round(Nw) * Nc)
        # print(start, end, N, Nc, Nw, np.round(Nw), new_end)     
        
        harmonic_magnitudes = []
        harmonics = Harmonics(fs=file.sampling_frequency, fn=file.line_frequency)
        harmonic_magnitudes.append(harmonics.harmonic_frequencies)
        
        harmonic_magnitudes.append(harmonics.estimate_harmonics(ia_signal[start:new_end]))
        harmonic_magnitudes.append(harmonics.estimate_harmonics(ib_signal[start:new_end]))
        harmonic_magnitudes.append(harmonics.estimate_harmonics(ic_signal[start:new_end]))
        harmonic_magnitudes.append(harmonics.estimate_harmonics(va_signal[start:new_end]))
        harmonic_magnitudes.append(harmonics.estimate_harmonics(vb_signal[start:new_end]))
        harmonic_magnitudes.append(harmonics.estimate_harmonics(vc_signal[start:new_end]))
         
        total_frequencies = len(harmonics.harmonic_frequencies)
        harmonic_values = []
        for i in range(total_frequencies):
            harmonic = {}
            harmonic["harmonic"] = i
            harmonic["ia"] = harmonic_magnitudes[1][i]
            harmonic["ib"] = harmonic_magnitudes[2][i]
            harmonic["ic"] = harmonic_magnitudes[3][i]
            harmonic["va"] = harmonic_magnitudes[4][i]
            harmonic["vb"] = harmonic_magnitudes[5][i]
            harmonic["vc"] = harmonic_magnitudes[6][i]
         
            harmonic_values.append(harmonic)

        # selected_phasors = {"phasors": split_phasors} 
        # return Response(json.dumps(selected_phasors))
        
        selected_harmonics = {"harmonics": harmonic_values} 
        return Response(json.dumps(selected_harmonics))
        
        # return Response("OK")



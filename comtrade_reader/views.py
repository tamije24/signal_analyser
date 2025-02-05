from django.conf import settings
from django.db.models.aggregates import Count
from django.db import transaction
import numpy as np
import json
from datetime import datetime, timedelta
# import logging

# from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly, IsAdminUser, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import AnalogSignal, AnalogSignalResampled, DigitalSignal, DigitalSignalResampled, Project, File, AnalogChannel, DigitalChannel
from .serializers import ProjectSerializer, CreateProjectWithFilesSerializer, FileSerializer, CreateFileSerializer, AnalogChannelSerializer, DigitalChannelSerializer, ProjectUpdateSerialiser

from utilities.handle_comtrade import ReadComtrade
from utilities.dft_phasors import DFTPhasors
from utilities.harmonics import Harmonics
from utilities.resample_signals import ResampleSignals

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
 
class AnalogSignalView(APIView):
    http_method_names = ['get', 'head', 'options']
    # renderer_classes = [JSONRenderer]
    
    def get(self, request, id, src):    
        if src == 1:
            analog_signals = list(AnalogSignal.objects.filter(file_id=id).order_by('time_signal'))
        else:
            analog_signals = list(AnalogSignalResampled.objects.filter(file_id=id).order_by('time_signal'))
        
        ia_signal = [item.ia_signal for item in analog_signals]
        ib_signal = [item.ib_signal for item in analog_signals]
        ic_signal = [item.ic_signal for item in analog_signals]
        in_signal = [item.in_signal for item in analog_signals]
        va_signal = [item.va_signal for item in analog_signals]
        vb_signal = [item.vb_signal for item in analog_signals]
        vc_signal = [item.vc_signal for item in analog_signals]
        time_signal = [item.time_signal for item in analog_signals]
        time_stamp = [item.time_stamp for item in analog_signals]
        
        # print(time_signal)
        # print(ia_signal)
        
        total_samples = len(ia_signal)
        # print(total_samples)
        
        # signals = analog_signals
        signals = []
        for i in range(total_samples):
            signal = {}
            signal["ia_signal"] = np.double(ia_signal[i])
            signal["ib_signal"] = np.double(ib_signal[i])
            signal["ic_signal"] = np.double(ic_signal[i])
            signal["in_signal"] = np.double(in_signal[i])
            signal["va_signal"] = np.double(va_signal[i])
            signal["vb_signal"] = np.double(vb_signal[i])
            signal["vc_signal"] = np.double(vc_signal[i])
            signal["time_signal"] = np.double(time_signal[i])
            signal["time_stamp"] = time_stamp[i]
            signals.append(signal)
        
        my_signals = {"signals": signals, "file": id} 
        
        # print(my_signals)
        
        return Response(json.dumps(my_signals)) 
     
class DigitalSignalView(APIView):
    http_method_names = ['get', 'head', 'options']
    # renderer_classes = [JSONRenderer]
     
    def get(self, request, id, src):    
        if src == 1:
            digital_signals = list(DigitalSignal.objects.filter(file_id=id).order_by('time_signal'))
        else:
            digital_signals = list(DigitalSignalResampled.objects.filter(file_id=id).order_by('time_signal'))
            
        d1_signal = [item.d1_signal for item in digital_signals]
        d2_signal = [item.d2_signal for item in digital_signals]
        d3_signal = [item.d3_signal for item in digital_signals]
        d4_signal = [item.d4_signal for item in digital_signals]
        d5_signal = [item.d5_signal for item in digital_signals]
        d6_signal = [item.d6_signal for item in digital_signals]
        d7_signal = [item.d7_signal for item in digital_signals]
        d8_signal = [item.d8_signal for item in digital_signals]
        d9_signal = [item.d9_signal for item in digital_signals]
        d10_signal = [item.d10_signal for item in digital_signals]
        d11_signal = [item.d11_signal for item in digital_signals]
        d12_signal = [item.d12_signal for item in digital_signals]
          
        total_samples = len(d1_signal)
        signals = []
        for i in range(total_samples):
            signal = {}
            signal["d1_signal"] = int(d1_signal[i])
            signal["d2_signal"] = int(d2_signal[i])
            signal["d3_signal"] = int(d3_signal[i])
            signal["d4_signal"] = int(d4_signal[i])
            signal["d5_signal"] = int(d5_signal[i])
            signal["d6_signal"] = int(d6_signal[i])
            signal["d7_signal"] = int(d7_signal[i])
            signal["d8_signal"] = int(d8_signal[i])
            signal["d9_signal"] = int(d9_signal[i])
            signal["d10_signal"] = int(d10_signal[i])
            signal["d11_signal"] = int(d11_signal[i])
            signal["d12_signal"] = int(d12_signal[i])
            signals.append(signal)
        
        my_signals = {"signals": signals, "file": id} 
        return Response(json.dumps(my_signals)) 

class PhasorView(APIView):
    http_method_names = ['get', 'head', 'options']
    # renderer_classes = [JSONRenderer]
    
    def get(self, request, id, src): 
        # print(id)   
        file_list = list(File.objects.filter(file_id=id).order_by('file_id'))  
        # print(file_list)  
        file = file_list[0]
        
        if src == 1:
            analog_signals = list(AnalogSignal.objects.filter(file_id=id).order_by('time_signal'))
        else:
            analog_signals = list(AnalogSignalResampled.objects.filter(file_id=id).order_by('time_signal'))
                
        ia_signal = [item.ia_signal for item in analog_signals]
        ib_signal = [item.ib_signal for item in analog_signals]
        ic_signal = [item.ic_signal for item in analog_signals]
        in_signal = [item.in_signal for item in analog_signals]
        va_signal = [item.va_signal for item in analog_signals]
        vb_signal = [item.vb_signal for item in analog_signals]
        vc_signal = [item.vc_signal for item in analog_signals]
        
        phasors = []
        # print(file.sampling_frequency, file.line_frequency)
        dftphasor = DFTPhasors(fs=file.sampling_frequency, fn=file.line_frequency)
        
        phasors.append(dftphasor.estimate_dft_phasors(ia_signal))
        phasors.append(dftphasor.estimate_dft_phasors(ib_signal))
        phasors.append(dftphasor.estimate_dft_phasors(ic_signal))
        phasors.append(dftphasor.estimate_dft_phasors(in_signal))
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
            split_phasor["in-mag"] = np.absolute(phasors[3][i])
            split_phasor["in-ang"] = np.angle(phasors[3][i])
            split_phasor["va-mag"] = np.absolute(phasors[4][i])
            split_phasor["va-ang"] = np.angle(phasors[4][i])
            split_phasor["vb-mag"] = np.absolute(phasors[5][i])
            split_phasor["vb-ang"] = np.angle(phasors[5][i])
            split_phasor["vc-mag"] = np.absolute(phasors[6][i])
            split_phasor["vc-ang"] = np.angle(phasors[6][i])
         
            split_phasors.append(split_phasor)

        selected_phasors = {"phasors": split_phasors, "file": id} 
        return Response(json.dumps(selected_phasors))
    
class HarmonicsView(APIView):
    http_method_names = ['get', 'head', 'options']
    # renderer_classes = [JSONRenderer]
    
    def get(self, request, id, start, end, src):    
        file_list = list(File.objects.filter(file_id=id))    
        file = file_list[0]
        
        if src == 1:
            analog_signals = list(AnalogSignal.objects.filter(file_id=id).order_by('time_signal'))
        else:
            analog_signals = list(AnalogSignalResampled.objects.filter(file_id=id).order_by('time_signal'))
        
        ia_signal = [item.ia_signal for item in analog_signals]
        ib_signal = [item.ib_signal for item in analog_signals]
        ic_signal = [item.ic_signal for item in analog_signals]
        in_signal = [item.in_signal for item in analog_signals]
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
        harmonic_magnitudes.append(harmonics.estimate_harmonics(in_signal[start:new_end]))
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
            harmonic["in"] = harmonic_magnitudes[4][i]
            harmonic["va"] = harmonic_magnitudes[5][i]
            harmonic["vb"] = harmonic_magnitudes[6][i]
            harmonic["vc"] = harmonic_magnitudes[7][i]
         
            harmonic_values.append(harmonic)

        # selected_phasors = {"phasors": split_phasors} 
        # return Response(json.dumps(selected_phasors))
        
        selected_harmonics = {"harmonics": harmonic_values, "file": id} 
        return Response(json.dumps(selected_harmonics))
        
        # return Response("OK")

class ResampleView(APIView):

    #permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'head', 'options']
    
    def get(self, request, id, fsnew):
              
        # Read file information
        file_list = list(File.objects.filter(file_id=id).order_by('file_id'))  
        file = file_list[0]
        resampled_frequency = file.resampled_frequency
        fsold = file.sampling_frequency
        
        # Check if resampling already done        
        resampled_signals = list(AnalogSignalResampled.objects.filter(file_id=id).order_by('time_signal'))
        
        # Check if resampling already done for this file
        if resampled_frequency == fsnew and len(resampled_signals) > 0:
            # Resampling already done
            return Response(id, status=status.HTTP_201_CREATED)

        else:        
            # Do resampling
            with transaction.atomic(): 
                
                # If resampled signals already present (different sampling frequency) delete the records
                resampled_signals = list(AnalogSignalResampled.objects.filter(file_id=id).order_by('time_signal'))
                for i in range(len(resampled_signals)):
                    resampled_signals[i].delete()
                
                resampled_signals = list(DigitalSignalResampled.objects.filter(file_id=id).order_by('time_signal'))
                for i in range(len(resampled_signals)):
                    resampled_signals[i].delete()
                
                # READ ANALOG SIGNALS
                analog_signals = list(AnalogSignal.objects.filter(file_id=id).order_by('time_signal'))
                ia_signal = [item.ia_signal for item in analog_signals]
                ib_signal = [item.ib_signal for item in analog_signals]
                ic_signal = [item.ic_signal for item in analog_signals]
                in_signal = [item.in_signal for item in analog_signals]
                va_signal = [item.va_signal for item in analog_signals]
                vb_signal = [item.vb_signal for item in analog_signals]
                vc_signal = [item.vc_signal for item in analog_signals]
                time_signal = [item.time_signal for item in analog_signals]
                time_stamp = [item.time_stamp for item in analog_signals]
            
                # RESAMPLE ANALOG SIGNALS
                t_step = time_signal[1] - time_signal[0]
                resampling = ResampleSignals(fs_new=fsnew, fs_old=fsold, t_step=t_step)
            
                new_ia_signal = resampling.resample_by_interpolation(ia_signal)
                new_ib_signal = resampling.resample_by_interpolation(ib_signal)
                new_ic_signal = resampling.resample_by_interpolation(ic_signal)
                new_in_signal = resampling.resample_by_interpolation(in_signal)
                new_va_signal = resampling.resample_by_interpolation(va_signal)
                new_vb_signal = resampling.resample_by_interpolation(vb_signal)
                new_vc_signal = resampling.resample_by_interpolation(vc_signal)
                
                new_time_signal = np.linspace(min(time_signal), max(time_signal), len(new_ia_signal))
            
                total_samples = len(new_ia_signal)
            
                st_time = datetime.fromisoformat(str(file.start_time_stamp ))
                t_step_new = float(new_time_signal[1] - new_time_signal[0])
                delta = timedelta(microseconds=t_step_new*1000000.0)
                    
                analog_samples = []    
                for i in range(total_samples):
                    temp = (st_time + i*delta).strftime('%d/%m/%Y, %H:%M:%S.%f')
                    analog_samples.append(AnalogSignalResampled(
                        sample_id = "{}-{}".format(id, i),
                        file_id = id,
                        time_signal = np.double(new_time_signal[i]),
                        ia_signal = np.double(new_ia_signal[i]),
                        ib_signal = np.double(new_ib_signal[i]),
                        ic_signal = np.double(new_ic_signal[i]),
                        in_signal = np.double(new_in_signal[i]),
                        va_signal = np.double(new_va_signal[i]),
                        vb_signal = np.double(new_vb_signal[i]),
                        vc_signal = np.double(new_vc_signal[i]),
                        time_stamp = temp,
                    )) 
                    
                # Save to table
                AnalogSignalResampled.objects.bulk_create(analog_samples)
                              
                # READ DIGITAL SIGNALS
                digital_signals = list(DigitalSignal.objects.filter(file_id=id).order_by('time_signal'))
                d1_signal = [item.d1_signal for item in digital_signals]
                d2_signal = [item.d2_signal for item in digital_signals]
                d3_signal = [item.d3_signal for item in digital_signals]
                d4_signal = [item.d4_signal for item in digital_signals]
                d5_signal = [item.d5_signal for item in digital_signals]
                d6_signal = [item.d6_signal for item in digital_signals]
                d7_signal = [item.d7_signal for item in digital_signals]
                d8_signal = [item.d8_signal for item in digital_signals]
                d9_signal = [item.d9_signal for item in digital_signals]
                d10_signal = [item.d10_signal for item in digital_signals]
                d11_signal = [item.d11_signal for item in digital_signals]
                d12_signal = [item.d12_signal for item in digital_signals]
                
                # RESAMPLE DIGITAL SIGNALS
                new_d1_signal = resampling.resample_by_interpolation(d1_signal)
                new_d2_signal = resampling.resample_by_interpolation(d2_signal)
                new_d3_signal = resampling.resample_by_interpolation(d3_signal)
                new_d4_signal = resampling.resample_by_interpolation(d4_signal)
                new_d5_signal = resampling.resample_by_interpolation(d5_signal)
                new_d6_signal = resampling.resample_by_interpolation(d6_signal)
                new_d7_signal = resampling.resample_by_interpolation(d7_signal)
                new_d8_signal = resampling.resample_by_interpolation(d8_signal)
                new_d9_signal = resampling.resample_by_interpolation(d9_signal)
                new_d10_signal = resampling.resample_by_interpolation(d10_signal)
                new_d11_signal = resampling.resample_by_interpolation(d11_signal)
                new_d12_signal = resampling.resample_by_interpolation(d12_signal)
                
                digital_samples = []
                for i in range(total_samples):
                    digital_samples.append(DigitalSignalResampled(
                        sample_id = "{}-{}".format(id, i),    
                        file_id = id,
                        time_signal = np.double(new_time_signal[i]),
                        d1_signal = new_d1_signal[i],
                        d2_signal = new_d2_signal[i],
                        d3_signal = new_d3_signal[i],
                        d4_signal = new_d4_signal[i],
                        d5_signal = new_d5_signal[i],
                        d6_signal = new_d6_signal[i],
                        d7_signal = new_d7_signal[i],
                        d8_signal = new_d8_signal[i],
                        d9_signal = new_d9_signal[i],
                        d10_signal = new_d10_signal[i],
                        d11_signal = new_d11_signal[i],
                        d12_signal = new_d12_signal[i],
                    )) 
                    
                # Save to table
                DigitalSignalResampled.objects.bulk_create(digital_samples)
                
                # Update resampled frequency value
                file.resampled_frequency = fsnew
                file.save()    
        
        return Response(id, status=status.HTTP_201_CREATED)
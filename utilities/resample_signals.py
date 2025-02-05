import numpy as np
from numpy.fft import fft, fftshift, fftfreq
import matplotlib.pyplot as plt


class ResampleSignals():
    
    def __init__(self, **kwargs):        
        fs_new = kwargs['fs_new']
        fs_old = kwargs['fs_old']
        t_step = kwargs['t_step']
        
        factor = fs_new / fs_old
        
        self.output_step = float(t_step) / factor
        self.input_step = float(t_step)
           
    def resample_by_interpolation(self, signal):

        output_step = self.output_step
        input_step = self.input_step
        
        scale = input_step / output_step
        # calculate new length of sample
        n = round(len(signal) * scale)
        
        samples = np.array(signal,dtype=float)
        resampled_sg = np.interp(
            np.linspace(0, 1.0, n),  # where to interpret
            np.linspace(0.0, 1.0, len(signal)),  # known positions
            samples,  # known data points
        )
        return resampled_sg    
        
 

   
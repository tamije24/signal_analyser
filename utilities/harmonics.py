import numpy as np
from numpy.fft import fft, fftshift, fftfreq
import matplotlib.pyplot as plt


class Harmonics():
    
    def __init__(self, **kwargs):
        self.fn = kwargs['fn']
        self.fs = kwargs['fs']
        N = int(self.fs /self.fn)
        self.N = N
        
        # f_step = self.fs / N
        # f = np.linspace(0, (N-1)*f_step, N)
        # self.harmonic_frequencies = f[0:int(N/2+1)] 
        
        self.harmonic_frequencies = np.arange(0, self.fs/2+1, self.fn)
                      
    def estimate_harmonics(self, samples):   
        
        arr_samples = np.array(samples, dtype='float32')
        N = len(arr_samples)   # Total window size (no of samples) 

        fs = self.fs           # Sampling frequency (Hz)
        fn = self.fn           # Nominal frequency (Hz) 
        Nc = fs/fn             # Samples / cycle
        Nw = N / Nc            # No of cycles of data available

        # Harmonics using DFT
        freq = np.arange(0, fs/2+1, fn)
        max_no_of_freq_components = int(N/2)
        X = np.zeros(int(len(freq)), dtype=np.complex128)

        if N > 0:
            count = 0
            for m in np.arange(0,max_no_of_freq_components,Nw):
                for n in range(N):
                    X[count] = X[count] + arr_samples[n] * (np.sin(2*np.pi*n*m/N) - 1j*np.cos(2*np.pi*n*m/N))
                count = count + 1
        
            harmonics = np.abs(X) / (N/2)
        else:
            harmonics = np.abs(X)
             
        # print(N, Nc, Nw)     
        # print(freq)
        # print(max_no_of_freq_components)
        # print(len(X))
        # print(np.abs(X)/(N/2))
        return harmonics
        

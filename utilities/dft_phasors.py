import math
import numpy as np
import decimal 
# import matplotlib.pyplot as plt

class DFTPhasors():
    
    def __init__(self, **kwargs):
        self.fn = kwargs['fn']
        self.fs = kwargs['fs']
        [self.real_coeff, self.imag_coeff] = self.calculate_filter_coefficients(self.fs,self.fn)
        
    def calculate_filter_coefficients(self,fs,fn):
        pi = np.pi    
        Wn = 2*pi*fn
        Ts = 1/fs

        n = np.arange(0.5,fs/fn)
        cr = np.sin(Wn*n*Ts) / (len(n)/2)
        ci = np.cos(Wn*n*Ts) / (len(n)/2)     
        
        for i in range(len(cr)):
            cr[i] = decimal.Decimal(cr[i])
            ci[i] = decimal.Decimal(ci[i])
            
        return [cr, ci]
    
    def estimate_dft_phasors(self, samples):
        L = len(samples)
        N = len(self.real_coeff)
                
        estimated_phasor = np.zeros((L), dtype=np.complex128)
        
        # Correlation using DFT algorithm
        moving_data_window = np.zeros((N))
        for n in range(L):
            moving_data_window = [item for item in moving_data_window[1:]]            
            moving_data_window = np.append(moving_data_window, float(samples[n]))
            
            phasor_real = np.sum(np.multiply(self.real_coeff, moving_data_window)) / math.sqrt(2)
            phasor_imag = np.sum(np.multiply(self.imag_coeff, moving_data_window)) / math.sqrt(2)
                             
            estimated_phasor[n] = phasor_real + phasor_imag*1j
        
        return estimated_phasor    
        
                   
# pi = np.pi

# # nominal frequency
# fn = 50       
# # sampling rate
# fs = 1000
# # sampling interval
# ts = 1.0/fs
# t = np.arange(0,0.1,ts)

# h = 1
# samples = 10*np.sin(2*pi*h*fn*t)   

# dftphasor = DFTPhasors(samples=samples, fs=fs, fn=fn)
# phasors_values = dftphasor.estimate_dft_phasors()

# plt.figure(1)     
# plt.subplot(211)
# plt.plot(t,samples)

# plt.subplot(212)
# plt.plot(t,np.absolute(phasors_values))

# plt.show()
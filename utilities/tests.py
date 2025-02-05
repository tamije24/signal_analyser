
# Create your tests here.

import numpy as np
from numpy.fft import fft, fftshift, fftfreq
from matplotlib import pyplot as plt

# t0 = 0              # Start time 
# fs = 5000           # Sampling rate (Hz)
# ts = 1/fs
# fn = 50

# Nw = 7.5
# N = int(Nw * (fs/fn))
# tmax = ts*N          # End time       

# t = np.arange(t0, tmax, ts)
# signal = 0*20 + 10*np.sin(2 *np.pi * fn * t) 
# # + 5*np.sin(2 * np.pi * 3 * fn * t) + 4*np.sin(2 * np.pi * 4 * fn * t) + 5*np.sin(2 * np.pi * 5 * fn * t) + 5*np.sin(2 * np.pi * 10 * fn * t)

# Nc = fs/fn
# # print(N)
# # print(Nc)
# # print(N/Nc)

# F = fftshift(fft(signal))
# freqs = fftshift(fftfreq(len(t), ts))

# # Harmonics using DFT
# freq = np.arange(0, fs/2+1, fn)
# no_of_freq_components = int(N/2)
# X = np.zeros(int(no_of_freq_components/Nw+1), dtype=np.complex128)

# # print(freq)
# # print(no_of_freq_components)
# # print(len(X))

# count = 0
# for m in np.arange(0,no_of_freq_components,Nw):
#     for n in range(N):
#         X[count] = X[count] + signal[n] * (np.sin(2*np.pi*n*m/N) - 1j*np.cos(2*np.pi*n*m/N))
#     count = count + 1
 
# X[0] = X[0] / 2     # DC component magnitude is double 
  
# print("DC: ", round(np.abs(X[0])/(N/2),2))  
# print("1: ", round(np.abs(X[1])/(N/2),2)) 
# print("2: ", round(np.abs(X[2])/(N/2),2)) 
# print("3: ", round(np.abs(X[3])/(N/2),2)) 
# print("4: ", round(np.abs(X[4])/(N/2),2)) 
# print("5: ", round(np.abs(X[5])/(N/2),2)) 
# print("6: ", round(np.abs(X[6])/(N/2),2)) 
# print("7: ", round(np.abs(X[7])/(N/2),2)) 
# print("8: ", round(np.abs(X[8])/(N/2),2)) 
# print("9: ", round(np.abs(X[9])/(N/2),2)) 
# print("10: ", round(np.abs(X[10])/(N/2),2)) 
        
# # print(X)        
# # print(np.abs(X))        
# # print(np.abs(X)/(N/2))
# # print(len(X))
# # print(len(range(no_of_freq_components)))

# # # print(len(t)/fs)
# # # print(len(freqs))
# # # print(len(F))

# # # print(freqs)
# # print(np.arange(0,a)*const)
# # print(np.abs(X[0])/(N/2))
# # print(np.abs(X[1])/(N/2))
# # print(np.abs(X[2])/(N/2))

# fig, axs = plt.subplots(4,1)
# axs[0].plot(t, signal)
# axs[0].set_title("Signal")

# axs[1].plot(freqs, 2*np.abs(F)/len(t))
# axs[1].set_title("FFT-Spectrum")

# axs[2].stem(freq, np.abs(X)/(N/2))
# axs[2].set_title("DFT-Spectrum")

# c_sin_1 = np.zeros(N)
# c_cos_1 = np.zeros(N)
# c_sin_2 = np.zeros(N)
# c_cos_2 = np.zeros(N)

# for n in range(N):
#     c_sin_1[n] = np.sin(2*np.pi*n*1/N)
#     c_cos_1[n] = np.cos(2*np.pi*n*1/N)
#     c_sin_2[n] = np.sin(2*np.pi*n*2/N)
#     c_cos_2[n] = np.cos(2*np.pi*n*2/N)
    
# fig, axs2 = plt.subplots(5,1)
# axs2[0].plot(t, signal)
# axs2[0].set_title("Signal")

# axs2[1].plot(t, c_sin_1)
# axs2[1].set_title("Sine coeffcients")

# axs2[2].plot(t, c_cos_1)
# axs2[2].set_title("Cosine coeffcients")

# axs2[3].plot(t, c_sin_2)
# axs2[3].set_title("Sine coeffcients")

# axs2[4].plot(t, c_cos_2)
# axs2[4].set_title("Cosine coeffcients")

# plt.tight_layout()
# plt.show()



# # # axs[1].set_xlim((-1000, 1000))
# # # axs[1].set_xticks(np.arange(-100,100,20))


def resample_by_interpolation(sig, output_step, input_step, x_range=[0, None] ):

    scale = input_step / output_step
    # calculate new length of sample
    n = round(len(sig) * scale)

    resampled_sg = np.interp(
        np.linspace(0, 1.0, n),  # where to interpret
        np.linspace(0.0, 1.0, len(sig)),  # known positions
        sig,  # known data points
    )
    return resampled_sg


x = np.linspace(-2, 8*np.pi, 50)
y = np.sin(x)
output_step, input_step = ((x[1]-x[0])/4.2, x[1]-x[0])
new_y = resample_by_interpolation(y, output_step, input_step, x_range= [2.5, 25])
new_x = np.linspace(min(x), max(x), len(new_y))


plt.figure(1)
plt.plot(x, y, '-*')
plt.plot(new_x, new_y, 'x')
plt.show()

plt.figure(2)
plt.plot(y)
plt.plot(new_y)

print(len(x), len(y))
print(len(new_x), len(new_y))
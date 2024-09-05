import numpy as np

class Sequence():
    
    def __init__(self, **kwargs):
        self.ia_phasor = np.array(kwargs['ia'])
        self.ib_phasor = np.array(kwargs['ib'])
        self.ic_phasor = np.array(kwargs['ic'])
        
        self.va_phasor = np.array(kwargs['va'])
        self.vb_phasor = np.array(kwargs['vb'])
        self.vc_phasor = np.array(kwargs['vc'])
        
        
    def calculate_sequence_components(self, sig_a, sig_b, sig_c):
        PI = np.pi
        a = np.exp(1j*2*PI/3)
           
        zero_seq = np.add(sig_a, sig_b, sig_c) * (1/3) 
        pos_seq = np.add(sig_a, a*sig_b, (a*a)*sig_c) * (1/3) 
        neg_seq = np.add(sig_a, (a*a)*sig_b, a*sig_c) * (1/3) 
        
        return [zero_seq, pos_seq, neg_seq]

    def get_sequence_current_components(self):
        return self.calculate_sequence_components(self.ia_phasor, 
                                           self.ib_phasor, 
                                           self.ic_phasor)
    
    def get_sequence_voltage_components(self):
        return self.calculate_sequence_components(self.va_phasor, 
                                           self.vb_phasor, 
                                           self.vc_phasor)        
        
    def get_sequence_components(self):
        [i0_phasor, i1_phasor, i2_phasor] = self.get_sequence_current_components()
        [v0_phasor, v1_phasor, v2_phasor] = self.get_sequence_voltage_components()
        
        return [i0_phasor, i1_phasor, i2_phasor, v0_phasor, v1_phasor, v2_phasor]    
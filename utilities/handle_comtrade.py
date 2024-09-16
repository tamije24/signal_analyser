from numpy import shape
from . import comtrade

class ReadComtrade():
    
    def __init__(self, **kwargs):
        self.cfg_file = kwargs['cfg_file']
        self.dat_file = kwargs['dat_file']
        self.comtrade_record = comtrade.load(self.cfg_file, self.dat_file)
        
    def read_comtrade_config_data(self):
        analog_channels = [ { "channel_id": channel.n,
                              "channel_name": channel.name,
                              "phase": channel.ph,
                              "unit": channel.uu,
                              "primary": channel.primary,
                              "secondary": channel.secondary,
                              "pors": channel.pors,
                            } for channel in self.comtrade_record.cfg.analog_channels ]
        
        digital_channels = [ { "channel_id": channel.n,
                              "channel_name": channel.name,
                              "normal_state": channel.y
                            } for channel in self.comtrade_record.cfg.status_channels ] 
        
        file_info = {
            "station_name": self.comtrade_record.station_name,
            "analog_channel_count": self.comtrade_record.analog_count,
            "digital_channel_count": self.comtrade_record.status_count,
            "start_time_stamp": self.comtrade_record.start_timestamp,
            "trigger_time_stamp": self.comtrade_record.trigger_timestamp,
            "line_frequency": self.comtrade_record.frequency,
            "sampling_frequency": self.comtrade_record.cfg.sample_rates[0][0],
        }    
        
        #     #TODO sampling rate to be updated from time signal read
        
        return [file_info, analog_channels, digital_channels]
 

    def read_comtrade_analog_signals(self):
        total_samples = self.comtrade_record.total_samples 
        time_signal = self.comtrade_record.time   
        analog_signals = self.comtrade_record.analog
        analog_channels_converted =  []
        
        i = 0
        for channel in self.comtrade_record.cfg.analog_channels:
            if channel.pors == "S" or channel.pors == "s":
                analog_channels_temp = [sample * channel.primary / channel.secondary for sample in analog_signals[i]]
            else:
                analog_channels_temp = analog_signals[i]    
                
            analog_channels_converted.append(analog_channels_temp)    
            i=i+1  
        
        return [total_samples, time_signal, analog_channels_converted]
        
    def read_comtrade_digital_signals(self):
        total_samples = self.comtrade_record.total_samples 
        time_signal = self.comtrade_record.time   
        # digital_channels = self.comtrade_record.status_channel_ids
        digital_signals = self.comtrade_record.status
        
        return [total_samples, time_signal, digital_signals]     
        
    
        
      
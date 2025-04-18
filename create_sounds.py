import numpy as np
from scipy.io import wavfile

def create_laser_sound():
    
    duration = 0.1  
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = 1000
    waveform = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 10)
    waveform = np.int16(waveform * 32767)
    wavfile.write('snd/laser.wavpyt', sample_rate, waveform)

def create_explosion_sound():
    
    duration = 0.3
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    noise = np.random.normal(0, 1, len(t))
    waveform = noise * np.exp(-t * 5)
    waveform = np.int16(waveform * 32767)
    wavfile.write('snd/explosion.wav', sample_rate, waveform)

def create_powerup_sound():
    
    duration = 0.2
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = np.linspace(400, 800, len(t))
    waveform = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 2)
    waveform = np.int16(waveform * 32767)
    wavfile.write('snd/powerup.wav', sample_rate, waveform)

def create_background_music():
    
    duration = 5.0
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    
    melody = np.sin(2 * np.pi * 200 * t) * 0.3
    
    
    beat = np.sin(2 * np.pi * 2 * t) * 0.2
    
   
    waveform = melody + beat
    waveform = np.int16(waveform * 32767)
    wavfile.write('snd/background.wav', sample_rate, waveform)

if __name__ == '__main__':
    import ospy
    
   
    if not os.path.exists('snd'):
        os.makedirs('snd')
    
   
    create_laser_sound()
    create_explosion_sound()
    create_powerup_sound()
    create_background_music()
    
    print("Create Sounds!") 
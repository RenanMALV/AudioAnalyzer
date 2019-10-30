import pyaudio
import os
import struct
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
import time
from tkinter import TclError
import wave

# constants
CHUNK = 1024 * 2             # samples per frame
FORMAT = pyaudio.paInt16     # audio format (bytes per sample?)
CHANNELS = 1                # single channel for microphone 2 channels for wav
RATE =44100                 # samples per second
CHUNK_FREQ_VALIDA=int(CHUNK/2)     # frequencia valida = metade do sample RATE, 2000 para margem de erro
filename='audiocheck.net_sin_500Hz_-3dBFS_5s.wav'
CHUNK_PERFRAME_IN_WAV = 1024 * 2
DIVISOR_DE_AMPLITUDE = 128
THRESHOLD=0.3

# create matplotlib figure and axes
fig, (ax1, ax2) = plt.subplots(2, figsize=(15, 7))
fig.show()

# pyaudio class instance
p = pyaudio.PyAudio()

# stream object to get data from microphone
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

# variable for plotting
x = np.arange(0, 2 * CHUNK, 2)       # samples (waveform)
xf = np.linspace(0, RATE, CHUNK)     # frequencies (spectrum)

# create a line object with random data
line, = ax1.plot(x, np.random.rand(CHUNK), '-', lw=1)

# create semilogx line for spectrum
line_fft, = ax2.semilogx(xf, np.random.rand(CHUNK), '-', lw=1)

# format waveform axes
ax1.set_title('AUDIO WAVEFORM')
ax1.set_xlabel('samples')
ax1.set_ylabel('volume')
ax1.set_ylim(0, 255)
ax1.set_xlim(0, 2 * CHUNK)
plt.setp(ax1, xticks=[0, CHUNK, 2 * CHUNK], yticks=[0, 128, 255])

# format spectrum axes
ax2.set_xlim(20, RATE / 2)
ax2.set_ylim(0, 21)
print('stream started')

# open .wav file
wf = wave.open(filename, 'rb')

# for measuring frame rate
frame_count = 0
start_time = time.time()
LIM=0

while True:
    # binary data
    data = stream.read(CHUNK)  
    #data = wf.readframes(CHUNK_PERFRAME_IN_WAV)
    #stream.write(data)
        
    
    #data_int = struct.unpack(str(2 * CHUNK) + 'B', data)
    #print(data_int)
    # convert data to float, make np array,escala a aplitude, maxima de aproximadamente 25000, dividindo por 128, then offset it by 127
    data_int = np.frombuffer(data, dtype='h')
    #print(np.amax(data_int))
    data_np = np.array(data_int, dtype='h')/DIVISOR_DE_AMPLITUDE + 128

    # create np array and offset by 128
    #data_np = np.array(data_int, dtype='b')[::2] + 128
    #print(data_np)
    line.set_ydata(data_np)
    
    # compute FFT and update line
    yf = fft(data_int)
    # divide os valores da array correspondente a primeira parte da magnitude do resultado por 2 vezes a amplitude da onda vezes o tamanho do buffer
    scaled_data_fft = np.abs(yf[0:CHUNK])/(255 * 2 * CHUNK)
    #print(Pico_freq)
    #print(np.amax(scaled_data_fft))
    #print(scaled_data_fft)
    line_fft.set_ydata(scaled_data_fft)

    scaled_data_fft = scaled_data_fft[0:CHUNK_FREQ_VALIDA]
    #obtem o valor maximo de toda a range de frequencias
    max_freq_range_val = np.amax(scaled_data_fft)
    #verifica se este é um valor relevante que passa do limiar de ruido
    if max_freq_range_val>THRESHOLD:
        print(max_freq_range_val)
        #obtem o index da frequencia a qual possui o valor maximo acima
        Pico_freq, = np.where(scaled_data_fft == max_freq_range_val)
        print(Pico_freq, " at ", Pico_freq*21.533203125, " Hz")

    # update figure canvas
    try:
        #if LIM==0:
            fig.canvas.draw()
            fig.canvas.flush_events()
            frame_count += 1
            #LIM=6
        #LIM-=1
        
    except TclError:
        
        # calculate average frame rate
        frame_rate = frame_count / (time.time() - start_time)
        
        print('stream stopped')
        print('average frame rate = {:.0f} FPS'.format(frame_rate))
        break

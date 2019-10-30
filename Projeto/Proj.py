import numpy as np
import matplotlib.pyplot as plt
import struct
import pyaudio
import wave
import sys

filename = 'Gospel Of The Throttle by Minutes Til Midnight.wav'

# Set chunk size of 1024 samples per data frame
chunk = 1024

# Open the sound file 
wf = wave.open(filename, 'rb')
print(wf.getframerate())

# Create an interface to PortAudio
p = pyaudio.PyAudio()

# Open a .Stream object to write the WAV file to
# 'output = True' indicates that the sound will be played rather than recorded
stream = p.open(
    format = p.get_format_from_width(wf.getsampwidth()),
    channels = wf.getnchannels(),
    rate = wf.getframerate(),
    output = True,
    frames_per_buffer=chunk
    )

#print(wf.getnframes())

# Play the sound by writing the audio data to the stream
i=0
Samp_W = wf.getsampwidth()
print(Samp_W)

if Samp_W==2:
    Warp_factor = 127
elif Samp_W==3:
    Warp_factor = 32767

fig, ax = plt.subplots()
x= np.arange(0,2 * chunk,2)
line, = ax.plot(x, np.random.rand(chunk))
ax.set_xlim(0,1024)
ax.set_ylim(0,2*Warp_factor)
fig.show()
lim=20
while(i<=wf.getnframes()):
    data = wf.readframes(chunk)
    
    represent_data_int = np.array(struct.unpack(str(Samp_W*chunk) + 'H', data),dtype='h')[::2] + Warp_factor
    
    stream.write(data)
 
    i+=1024

    if lim==0:
        line.set_ydata(represent_data_int)
        fig.canvas.draw()
        fig.canvas.flush_events()
        lim=20
    lim-=1

# Close and terminate the stream
stream.close()
p.terminate()

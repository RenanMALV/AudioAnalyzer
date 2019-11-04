import pyaudio
import os
import struct
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
import time
import wave
from Analise import *
from Functions import *

def detect():
    global modo
    modo = Modo()

    # definindo variaveis e constantes

    if modo==0 or modo==2:
        CHUNK = 1024 * 2             # samples per frame
        FORMAT = pyaudio.paInt16     # audio format (bytes per sample?)
        CHANNELS = 1                # single channel for microphone 2 channels for wav
        RATE =44100                 # samples per second
        CHUNK_FREQ_VALIDA=int(CHUNK/2)     # frequencia valida = metade do sample RATE, 2000 para margem de erro
        filename = getFilename()
        CHUNK_PERFRAME_IN_WAV = 1024 * 2
        DIVISOR_DE_AMPLITUDE = 128
        THRESHOLD=0.3
        wf = wave.open(filename, 'rb')  # open .wav file
    else:
        CHUNK = 1024 * 2             # samples per frame
        FORMAT = pyaudio.paInt16     # audio format (bytes per sample?)
        CHANNELS = 1                # single channel for microphone 2 channels for wav
        RATE =44100                 # samples per second
        CHUNK_FREQ_VALIDA=int(CHUNK/2)     # frequencia valida = metade do sample RATE
        DIVISOR_DE_AMPLITUDE = 4
        THRESHOLD=0.19

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

    # create matplotlib figure and axes
    fig, (ax1, ax2) = plt.subplots(2, figsize=(15, 7))
    fig.show()

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
    print('Início da leitura')

    # for measuring frame rate
    frame_count = 0
    start_time = time.time()



    Pico_freq=-1    #indica arquivo vazio
    Record_Start=False
    Record_End=0

    while True:
        if modo==0 or modo==2:
            try:
                data = wf.readframes(CHUNK_PERFRAME_IN_WAV)
            except:
                ColetaDeDados(Pico_freq) #coleta o ultimo set de dados antes de inicializar as comparações
                break
        else:
            data = stream.read(CHUNK)

        # convert data to float, make np array,escala a aplitude maxima de aproximadamente 25000
        data_int = np.frombuffer(data, dtype='h')

        #create np array and offset by 128
        data_np = np.array(data_int, dtype='h')/DIVISOR_DE_AMPLITUDE + 128

        line.set_ydata(data_np)
        
        # compute FFT and update line
        yf = fft(data_int)
        # divide os valores da array correspondente a primeira parte da magnitude do resultado por 2 vezes a amplitude da onda vezes o tamanho do buffer
        scaled_data_fft = np.abs(yf[0:CHUNK])/(255 * 2 * CHUNK)
        line_fft.set_ydata(scaled_data_fft)

        scaled_data_fft = scaled_data_fft[0:CHUNK_FREQ_VALIDA]

        #obtem o valor maximo de toda a range de frequencias
        max_freq_range_val = np.amax(scaled_data_fft)
        #verifica se este é um valor relevante que passa do limiar de ruido
        if max_freq_range_val>THRESHOLD: #Possibilita a matriz final não guardar dados de ruidos
            Record_Start=True
            
            print(max_freq_range_val)
            #obtem o index da frequencia a qual possui o valor maximo acima
            Pico_freq, = np.where(scaled_data_fft == max_freq_range_val)
            print(Pico_freq, " at ", Pico_freq*21.533203125, " Hz")
            Record_End=time.time()
            #------------------------------------------------------------------------
            #inserir as frequencias de pico em uma matriz a qual cada linha da mesma seja a indicação de passagem de tempo em um determinado intervalo
            #ou seja, será feita a média aritimética das colunas de cada linha para saber a frequencia predominante em um determinado intervalo de tempo

            #inserção
            ColetaDeDados(Pico_freq)

            #------------------------------------------------------------------------    
        elif Record_Start:
            Pico_freq=0
            ColetaDeDados(Pico_freq)
            if modo==1 or modo==3:
                if (time.time()-Record_End)>2.5:
                    break
        # update figure canvas e sai do modo leitura quando a janela é fechada
        try:
            fig.canvas.draw()
            fig.canvas.flush_events()
            frame_count += 1
            
        except:

            ColetaDeDados(Pico_freq) #coleta o ultimo set de dados antes de inicializar as comparações
            break

    # calculate average frame rate
    frame_rate = frame_count / (time.time() - start_time)
    if modo==0 or modo==2:
        wf.close()
        plt.close('all')
    else:
        stream.close()
        plt.close('all')
    for i in getData_Arr():
        print(i)
    print('Fim da coleta do audio...')
    print('Número médio de quadros por segundo = {:.0f} FPS'.format(frame_rate))


#MAIN LOOP
print("/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\")
detect()
if modo==0 or modo==1:
    SaveInDB(getData_Arr())  #salva o padrão obtido no banco de dados do programa
else:
    print('Analisando os dados...')
    Compare()
os.system("reconhecimento.py")

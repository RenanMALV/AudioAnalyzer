import pyaudio
import os
import struct
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
import time
import wave

#Biblioteca de funcoes proprias do programa
from Analise import *
from Functions import *

def detect():
    global modo
    modo = Modo()

    # definindo variaveis e constantes

    if modo==0 or modo==2:
        CHUNK = 1024 * 2             # samples por frame
        FORMAT = pyaudio.paInt16     # Formato do audio -> bytes por sample
        CHANNELS = 1                # canais de audio (1 = Mono)
        RATE =44100                 # samples por segundo
        CHUNK_FREQ_VALIDA=int(CHUNK/2)     # frequencia valida = metade do sample RATE, ou seja, metade dos dados contidos em um chunk
        filename = getFilename()
        CHUNK_PERFRAME_IN_WAV = 1024 * 2    #Chunk para arquivos WAV -> mono
        DIVISOR_DE_AMPLITUDE = 128          #Constante para ajustar a amplitude do sinal
        THRESHOLD=0.3                       #Limiar para evitar a leitura de ruidos
        wf = wave.open(filename, 'rb')  # open .wav file
    else:
        CHUNK = 1024 * 2             # samples por frame
        FORMAT = pyaudio.paInt16     # Formato do audio -> bytes por sample
        CHANNELS = 1                # canais de audio (1 = Mono)
        RATE =44100                 # samples por segundo
        CHUNK_FREQ_VALIDA=int(CHUNK/2)     # frequencia valida = metade do sample RATE, ou seja, metade dos dados contidos em um chunk
        DIVISOR_DE_AMPLITUDE = 4            #Constante para ajustar a amplitude do sinal
        THRESHOLD=0.19                      #Limiar para evitar a leitura de ruidos

        # instanciando a classe pyaudio
        p = pyaudio.PyAudio()
        # objeto para obter os dados do microfone
        stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        output=True,
        frames_per_buffer=CHUNK
        )

    # criando figuras e eixos com matplotlib
    fig, (ax1, ax2) = plt.subplots(2, figsize=(15, 7))
    fig.show()

    # variaveis que irao ser plotadas
    x = np.arange(0, 2 * CHUNK, 2)       # samples, grafico de ondas 
    xf = np.linspace(0, RATE, CHUNK)     # frequencias, espectro de frequencias

    # inicializando uma linha
    line, = ax1.plot(x, np.random.rand(CHUNK), '-', lw=1)

    # Usando a função semilog no eixo X para plotar o espectro de flequencias
    line_fft, = ax2.semilogx(xf, np.random.rand(CHUNK), '-', lw=1)

    # formatando o grafico de ondas
    ax1.set_title('Gráfico de onda')
    ax1.set_xlabel('Samples')
    ax1.set_ylabel('Amplitude')
    ax1.set_ylim(0, 255)
    ax1.set_xlim(0, 2 * CHUNK)
    plt.setp(ax1, xticks=[0, CHUNK, 2 * CHUNK], yticks=[0, 128, 255])

    # formatando o espectrograma
    ax2.set_title('Espectrograma')
    ax2.set_xlim(20, RATE / 2)
    ax2.set_ylim(0, 21)
    ax2.set_xlabel('Frequência (Hz)')
    ax2.set_ylabel('Amplitude')
    print('Início da leitura')

    # medindo quantos frames por segundo estão sendo analizados
    frame_count = 0
    start_time = time.time()



    Pico_freq=-1    #indica arquivo vazio/inicio da coleta dos dados
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

        # converte os dados do buffer e os insere em uma array
        data_int = np.frombuffer(data, dtype='h')

        #cria uma array com os dados deslocados em 128 e com suas amplitudes ajustadas para posteriormente plotar no grafico de ondas
        data_np = np.array(data_int, dtype='h')/DIVISOR_DE_AMPLITUDE + 128

        line.set_ydata(data_np)
        
        # Faz a Transformada Rapida de Fourier
        yf = fft(data_int)

        # divide os valores da array correspondente a primeira parte da magnitude do resultado da FFT(frequencias validas) por:
        #2 vezes a amplitude máxima teorica da onda(subida e descida de sinal) vezes o tamanho do buffer de dados coletados
        scaled_data_fft = np.abs(yf[0:CHUNK])/(255 * 2 * CHUNK)

        #plotando no espectrograma
        line_fft.set_ydata(scaled_data_fft)

        #Separa as frequencias que sao relevantes para analise
        scaled_data_fft = scaled_data_fft[0:CHUNK_FREQ_VALIDA]

        #obtem o valor maximo de todo o campo de frequencias obtidas (Maximo global)
        max_freq_range_val = np.amax(scaled_data_fft)

        #verifica se este é um valor relevante que passa do limiar de ruido
        if max_freq_range_val>THRESHOLD: #Possibilita a matriz final não guardar dados de ruidos
            Record_Start=True
            
            print(max_freq_range_val)
            #obtem o indice da frequencia a qual possui o valor maximo acima
            Pico_freq, = np.where(scaled_data_fft == max_freq_range_val)
            #conta para descobrir a frequencia a partir do indice do buffer disponivel na pasta info->README.txt 
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
        # atualiza o canvas da figura e sai do modo leitura quando a janela é fechada
        try:
            fig.canvas.draw()
            fig.canvas.flush_events()
            frame_count += 1
            
        except:

            ColetaDeDados(Pico_freq) #coleta o ultimo set de dados antes de inicializar as comparações
            break

    # medindo quantos frames por segundo estão sendo analizados e terminando os plots
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

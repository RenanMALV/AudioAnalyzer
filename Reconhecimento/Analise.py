import time
import numpy as np
from Functions import *

#Matrizes para analise de dados
Coleta_Arr = np.array([-1])    #-1 sinaliza o começo da leitura na matriz DataXTime_Arr
DataXTime_Arr = [] #array aninhada pelos sets de array Coleta_Arr

#intervalo de tempo para coleta de dados
TempoColetaDeAmostras = 0.7
DeltaT = 0

def ColetaDeDados(Pico_freq):
    global DeltaT, Coleta_Arr
    if time.time() - DeltaT > TempoColetaDeAmostras:
        #aninha à matriz DataXTime_Arr a nova leitura neste intervalo de tempo
        DataXTime_Arr.append(Coleta_Arr)
        Coleta_Arr = np.array([Pico_freq])
        DeltaT = time.time()
    else:
        Coleta_Arr = np.append(Coleta_Arr, Pico_freq)

def getData_Arr():
    return DataXTime_Arr

def Compare():
    global DataXTime_Arr
    DataXTime_ArrList = []
    tam = len(DataXTime_Arr)
    ArrList = searchInDB()
    Match = []
    for i in ArrList:
        if i[0]>tam-2 and i[0]<tam+2:
            Match.append(i)
    if len(Match)>0:
        for i in Match:
            DataXTime_ArrList.append(getFromDB(i[1])) #i[1] -> Nome do arquivo, recebe uma lista de arrays que combinam com o padrão pesquisado
    else:
        print("Sem resultados que combinam!")
        return
    
    index = 0
    cont = 0
    MediaToCompare = []
    AcuraciaToCompare=[]
    media = 0

    for Row in DataXTime_Arr:
        for Col in Row:
            if Col!=0:
                cont += 1
                media += Col
        if cont==0:
            MediaToCompare.append(0)
        else:
            MediaToCompare.append(media/cont)
        cont = 0
        media = 0
    
    for Arr in DataXTime_ArrList:
        MediaAtual = []
        for Row in Arr:
            for Col in Row:
                if Col!=0:
                    cont += 1
                    media += Col
            if cont==0:
                MediaAtual.append(0)
            else:
                MediaAtual.append(media/cont)
            cont = 0
            media = 0
        Acuracia = []
        if (len(MediaToCompare))<(len(MediaAtual)):
            C=len(MediaToCompare)
            i=0
            while C>i:
                print(MediaToCompare[i],"<|>",MediaAtual[i])
                if MediaToCompare[i] == 0 and MediaAtual[i]==0:
                    Acuracia.append(1)
                elif MediaToCompare[i] == 0 or MediaAtual[i]==0:
                    Acuracia.append(0)
                else:
                    if MediaAtual[i]>MediaToCompare[i]:
                        Acuracia.append((MediaToCompare[i]/MediaAtual[i])) #acuracia da comparação -> maior valor -> 1 = Media de frequencias em um determinado tempo totalmente igual
                    else:
                        Acuracia.append((MediaAtual[i]/MediaToCompare[i])) #acuracia da comparação -> maior valor -> 1 = Media de frequencias em um determinado tempo totalmente igual
                i += 1
        else:
            A=len(MediaAtual)
            i=0
            while A>i:
                print(MediaToCompare[i],"<|>",MediaAtual[i])
                if MediaToCompare[i] == 0 and MediaAtual[i]==0:
                    Acuracia.append(1)
                elif MediaToCompare[i] == 0 or MediaAtual[i]==0:
                    Acuracia.append(0)
                else:
                    if MediaAtual[i]>MediaToCompare[i]:
                        Acuracia.append((MediaToCompare[i]/MediaAtual[i])) #acuracia da comparação -> maior valor -> 1 = Media de frequencias em um determinado tempo totalmente igual
                    else:
                        Acuracia.append((MediaAtual[i]/MediaToCompare[i])) #acuracia da comparação -> maior valor -> 1 = Media de frequencias em um determinado tempo totalmente igual
                i += 1
            
        AcuraciaToCompare.append(Acuracia)

    BestResult = [0,0] #melhor resultado com [índice,valor]  
    for Ac in AcuraciaToCompare:
        aux = 0
        cont = 0
        for Value in Ac:
            print("-------------", Value)
            if Value == 0:
                if Ac[cont-1]>0.8:
                    Value = 0.5
            cont += 1
            aux += Value
            print(Value)
        print(Ac,len(Ac))
        aux = aux/len(Ac) #Media das acuracias obtidas nos intervalos de tempo
        if BestResult[1]<aux:
            BestResult = [index,aux]
        print(Match[index])
        index += 1
    print(AcuraciaToCompare[BestResult[0]],len(AcuraciaToCompare[BestResult[0]]))
    print("Melhor resultado encontrado: ",Match[BestResult[0]][1],"Com " + str(BestResult[1]*100) + "% de confiabilidade")
    os.popen("explorer \"https://duckduckgo.com/?q=! "+Match[BestResult[0]][2]+"\"")

    

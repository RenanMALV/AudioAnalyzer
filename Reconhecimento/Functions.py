import wave
import numpy as np
import pickle
import os

def Modo():
    print("Selecione O modo:")
    print("Inserir no banco de dados Por arquivo   -> 0")
    print("Inserir no banco de dados Por microfone -> 1")
    print("Comparar por arquivo --------------------> 2")
    print("Comparar por microfone ------------------> 3")
    escolha = input()
    if escolha == "0" or escolha == "1" or escolha == "2" or escolha == "3":
        return int(escolha)
    else:
        print("Valor inválido")
        return Modo()

def getFilename():
    try:
        print("Insira o caminho do arquivo")
        filename=str(input())
        wf = wave.open(filename, 'rb')
        wf.close()
        return filename
    except:
        print("Diretório inválido")
        return getFilename()

def SaveInDB(Arr):
    print("insira um nome para o padrão obtido:")
    filename=str(input())+".freq"
    print("insira uma descrção para o padrão:")
    desc=str(input())
    FreqList = []
    #atualizando o indexador de arquivos
    direc = os.getcwd()+"\\BD\\FreqList.list"
    if os.path.getsize(direc) > 0:
        file = open(direc, 'rb') 
        FreqList = pickle.load(file)
        file.close()
    FreqList.append([len(Arr),filename,desc])
    file = open(direc, "wb") 
    pickle.dump(FreqList, file)
    file.close()
    #salvando
    direc = os.getcwd() + '\\BD\\' + filename
    file = open(direc, 'wb') 
    pickle.dump(Arr, file)
    file.close()
    print("Salvo com sucesso!")
    

def getFromDB(filename):
    direc = os.getcwd()+"\\BD\\"+filename
    file = open(direc, 'rb') 
    Arr = pickle.load(file)
    file.close()
    return Arr

def searchInDB():
    FreqList = []
    direc = os.getcwd()+"\\BD\\FreqList.list"
    if os.path.getsize(direc) > 0:
        file = open(direc, 'rb') 
        FreqList = pickle.load(file)
        file.close()
    return FreqList

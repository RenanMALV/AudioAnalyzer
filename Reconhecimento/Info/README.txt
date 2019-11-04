O espaço possivel de input de dados é 0 até 44100(rate)
O valor máximo de frequencia audivel possível em um arquivo é metade do rate, ou seja, 22050 Hz
se reduzirmos esse range de valores para um buffer de 2048 bytes teremos o fator 21.533203125, ou seja, se tivermos o valor 1 representado no buffer (de range 0 - 2047) isto equivalerá a uma frequencia de 21.533203125 Hz (de range 0 - 44100)

import pickle
import psutil
import socket
import time

info = ("\n -----------------------MENU------------------------------"
        "\n 1 - Informações da Máquina "
        "\n 2 - Informações de Arquivos "
        "\n 3 - Informações Processos Ativos "
        "\n 4 - Informações de Redes "
        "\n 5 - Sub Rede "
        "\n 6 - Sair "
        "\n ---------------------------------------------------------")


class Client:
    """Classe responsavel pelo lado do cliente"""

    def __init__(self):
        """Instanciando o cliente, conecta ele ao servidor"""

        self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.endereco = socket.gethostname()
        self.porta = 9997
        self.socket_client.connect((self.endereco, self.porta))
        self.menu = info
        print('Cliente iniciado')

    def formatar_cpu_mem(self, list):
        """Função que printa a lista formatada """
        text = ''
        for i in list:
            text = text + f'{round(i, 2)}'
        print(text)

    def formatar_processos_titulo(self):
        """Função que formata titulo dos processos :return:"""
        title = f'{" " * 2}PID {" " * 6}Mem.(%) Executável'

        print(title)

    def formatar_processos_texto(self, pid):
        """
            função que formata processos
        :return:
        """
        try:
            p = psutil.Process(pid)
            text = f'{pid:6d}'
            vms = p.memory_info().vms / 1024 / 1024
            text = text + f'{vms:10.2f} MB'
            text = text + " " + p.exe()
            print(text)
        except:
            pass

    def redes_formatada(self):
        """
            # Função que formata Redes
        :return:
        """
        title = '{:21}'.format("Ip")
        title = title + '{:27}'.format("Netmask")
        title = title + '{:27}'.format("MAC")
        print(title)

    def opcao1(self, msg1):
        self.socket_client.send(msg1.encode('utf-8'))
        recv = self.socket_client.recv(2048)

        lista = pickle.loads(recv)

        print(' Porcentagem %CPU:', lista['cpu_ram'][0])
        print('Porcentagem %MEM:', round(lista['cpu_ram'][1] * 100))

        load = lista['cpu_info']

        print('Arquitetura: ', load['arch'])
        print('Bits: ', load['bits'])

        nucleos = lista['proc_info']

        print('Núcleos Lógicos:', nucleos[0])

        print('%CPU por Núcleo', nucleos[1])

        print('Frequência:', nucleos[2])

        print('Núcleos Físicos:', nucleos[3])

        disco = lista['disc_info']

        print(" % de Disco Usado:", disco.percent, '%')

    def opcao2(self, msg1):
        self.socket_client.send(msg1.encode('utf-8'))
        recv = self.socket_client.recv(2048)
        list2 = pickle.loads(recv)
        title = '{:11}'.format("Tamanho")
        title = title + '{:27}'.format("Data de Modificação")
        title = title + '{:27}'.format("Data de Criação")
        title = title + "Nome"
        print(title)
        for i in list2:
            kb = list2[i][0] / 1000
            size = '{:10}'.format(str('{:.2f}'.format(kb) + ' KB'))
            print(size, time.ctime(list2[i][2]), " ", time.ctime(list2[i][1]), " ", i)
        time.sleep(1)

    def opcao3(self, msg1):
        self.socket_client.send(msg1.encode('utf-8'))
        recv = self.socket_client.recv(1024)
        dic = pickle.loads(recv)
        lista = psutil.pids()
        self.formatar_processos_titulo()
        for i in lista:
            self.formatar_processos_texto(i)
        time.sleep(2)

    def opcao4(self, msg1):
        self.socket_client.send(msg1.encode('utf-8'))
        recv = self.socket_client.recv(2048)
        dic_redes = pickle.loads(recv)
        self.redes_formatada()

        ethernet = []

        for key in dic_redes:
            if key.startswith('Ethernet'):
                ethernet.append(key)

        ip = dic_redes[ethernet[0]][1].address
        netmask = dic_redes[ethernet[0]][1].netmask
        mac = dic_redes[ethernet[0]][0].address
        print(ip, '      ', netmask, '              ', mac)
        time.sleep(2)

    def opcao5(self, msg1):
        self.socket_client.send(msg1.encode('utf-8'))
        ip_complete = input('Digite o Ip para verificar a sub-rede: ')

        portasInput = input('Deseja verificar as portas?[S/n]')

        ipPortas = {}

        while True:

            if portasInput.lower() == 's' or portasInput == '':
                ipPortas['portas'] = True
                break
            elif portasInput.lower() == 'n':
                ipPortas['portas'] = False
                break
            else:
                print('Por favor, digite S ou N')
                portasInput = input('Deseja verificar as portas?[S/n]')

        print('Por favor, aguarde')
        info_incomplete = ip_complete.split('.')
        info = ".".join(info_incomplete[0:3]) + '.'

        # LOADING ...
        ipPortas['ip'] = info

        info_complete = pickle.dumps(ipPortas)
        self.socket_client.send(info_complete)

        recv = self.socket_client.recv(100000000)

        sub_net = pickle.loads(recv)

        print("O teste será feito na sub rede: ", info)

        if isinstance(sub_net, dict):
            for hosts, ports in sub_net.items():

                if len(ports) == 0:
                    print('O host {} não tem portas abertas'.format(hosts))

                else:
                    print('O host {} tem as seguintes portas abertas{}'.format(hosts, ports))

        else:

            for host in sub_net:
                print(f'O host {host} está ativo')

    def opcao6(self, msg1):
        self.socket_client.send(msg1.encode('utf-8'))
        bytes = self.socket_client.recv(1024)
        self.socket_client.shutdown(socket.SHUT_RDWR)
        self.socket_client.close()


def main():
    cliente = Client()

    while True:
        print(cliente.menu)
        msg1 = input('digite a opção desejada: ')
        if msg1 == '1':
            cliente.opcao1(msg1)

        elif msg1 == '2':
            cliente.opcao2(msg1)

        elif msg1 == '3':
            cliente.opcao3(msg1)

        elif msg1 == '4':
            cliente.opcao4(msg1)

        elif msg1 == '5':
            cliente.opcao5(msg1)

        elif msg1 == '6':
            cliente.opcao6(msg1)
            break
        else:
            print('Opção Inválida')


if __name__ == '__main__':
    main()

import socket
import time
import serial


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", 8000))
server.listen(1)

s = serial.Serial("/dev/ttyACM1")

claves = ['11951', 'carlos']

while 1:
    print "Esperando clientes..."
    socket_cliente, datos_cliente = server.accept()
    print "conectado cliente:" + str(datos_cliente)
    seguir = True
    while seguir:
        peticion = socket_cliente.recv(1024)
        print(peticion)
        if peticion in claves:
            s.write('1')
        else:
            s.write('0')
        
        time.sleep(3)
        socket_cliente.close()
        break

server.close()

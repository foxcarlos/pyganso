import socket
import android

droid = android.Android()

servidor = droid.dialogGetInput('Servidor', 'Ingrese el Servidor').result

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#'foxcarlos.no-ip.biz'
server.connect((servidor, 8000))
mensaje = droid.dialogGetInput('Mensaje', 'Ingrese el Mensaje a Enviar').result
server.send(mensaje)


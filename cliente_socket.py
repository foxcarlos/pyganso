import socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(('10.121.3.41', 8000))
server.send('hola')

__author__ = 'cgarcia'

import zmq
import time
import os
import ConfigParser
import bottle
import sys
import pymongo
from bson.objectid import ObjectId
from os.path import join, dirname
from bottle import route, static_file, template
import datetime
import re

class enviarZMQ():
    def __init__(self):
        ruta_arch_conf = os.getcwdu()  # os.path.dirname(sys.argv[0])
        
        # NOTA: Es necesario que exista fuera de la ruta actual un directorio llamado pyloro
        fi = '../pyloro/pyloro.cfg'
        archivo_configuracion = os.path.join(ruta_arch_conf, fi)
        self.fc = ConfigParser.ConfigParser()
        self.fc.read(archivo_configuracion)
        self.zmqConectar()

    def zmqConectar(self):
        ''' Busca en el archivo de configuracion pyloro.cfg todos los 
        demonios servidores ZMQ y los conecta'''
        
        self.socket = ''
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        seccionDemonio = 'DEMONIOS'
        
        if self.fc.has_section(seccionDemonio):
            for demonios in self.fc.items(seccionDemonio):
                seccion, archivo = demonios
                seccionFinal = seccion.upper()
                if self.fc.has_section(seccionFinal):
                    listaPar = []
                    for var, par in self.fc.items(seccionFinal):
                        listaPar.append(par)
                    print(listaPar)               
                    ip_telefono, \
                    puerto_telefono, \
                    puerto_adb_forward, \
                    ip_demonio_zmq, \
                    puerto_demonio_zmq, \
                    serial_telefono = listaPar
                    servSock = 'tcp://{0}:{1}'.format(ip_demonio_zmq, puerto_demonio_zmq)
                    try:
                        self.socket.connect(servSock)
                        print('Conexion Satisfactoria con el servidor {0}'.format(servSock))
                    except:
                        print('Ocurrio un Error al momento de conectar al Socket Server {0}'.format(servSock))

    def enviar(self, telefono, mensaje):
        msg = '{0}^{1}'.format(telefono, mensaje)
        devuelve = True

        try:
            self.socket.send(msg)
        except zmq.ZMQError:
            e = sys.exc_info()[1]
            print(e)

        #Se recibe el mensaje de vuelta
        msg_in = self.socket.recv()            
        noEnviado, nombreServidor = msg_in.split(',')
        if int(noEnviado):
            devuelve = True
        else:
            devuelve = False
        return devuelve

app = enviarZMQ()

def buscarContactosListas(objetoUsuarioIdPasado):
    '''Este metodo busca dentro de la base de datos mongo
    todos los conmtactos y listas que pertenecen a un usuario
    del Sistema pasado como parametro'''

    server = pymongo.MongoClient('localhost', 27017)
    baseDatos = server.pyloroweb
    coleccionListas = baseDatos.listas
    coleccionContactos = baseDatos.contactos
    
    objetoUsuarioId = objetoUsuarioIdPasado
    
    #Aqui se buscan los contactos y las listas que pertecen al usuario que inico sesion para mostrarlos en los combobox
    #Tanto los contactos como las listas se deben mostrar solo los del usuario que inicio sesion
    nombresMostrar = [f['nombre'] for f in coleccionContactos.find({"usuario_id":objetoUsuarioId}).sort('nombre')]
    listasMostrar = [f['nombre_lista'] for f in coleccionListas.find({"usuario_id":objetoUsuarioId}).sort('nombre_lista')]
    return nombresMostrar, listasMostrar

def buscarGrupos():
    '''Este metodo busca dentro de la base de datos mongo
    todos los Grupos o listas'''

    server = pymongo.MongoClient('localhost', 27017)
    baseDatos = server.pyloroweb
    coleccionListas = baseDatos.listas
    
    usuario = bottle.request.get_cookie("account")
    if usuario != 'vacio':
        objetoUsuarioId = buscarUsuarioId(usuario)
        #Aqui se buscan los grupos para mostrarlos en el combobox
        gruposMostrar = [f['nombre_lista'] for f in coleccionListas.find({"usuario_id":objetoUsuarioId}).sort('nombre_lista')]
        return gruposMostrar
    else:
        cabecera = 'Lo Siento ...!'
        msg = 'Ud. no ha iniciado sesion en el servidor'
        return bottle.template('mensaje_login', {'cabecera':cabecera, 'mensaje':msg})


def buscarUsuarioId(usuario):
    '''parametros 1 string: usuario
    Este metodo busca el objetoId en mongodb del usuario que inicio
    sesion en el Sistema pyLoroWeb'''

    usuarioBuscar = usuario
    cliente = pymongo.MongoClient('localhost', 27017)
    baseDatos = cliente.pyloroweb
    coleccionUsuarios = baseDatos.usuarios                    
    buscarId = [f['_id'] for f in coleccionUsuarios.find({'usuario':usuarioBuscar})]
    objetoId = buscarId[0] if buscarId else ''
    return objetoId

def validaLogin(usuario, clave):
    ''' parametros recibidos 2:
    (string usuario, string clave)
    Metodo para validar el inicio de sesion
    contra la base de datos'''

    lcUsuario = usuario
    lcClave = clave
    accesoPermitido = False

    cliente = pymongo.MongoClient('localhost', 27017)
    baseDatos = cliente.pyloroweb
    coleccionUsuarios = baseDatos.usuarios
    
    buscar = coleccionUsuarios.find({'usuario':lcUsuario.lower(), 'clave':lcClave}).count()
    if buscar:
        bottle.response.set_cookie("account", usuario)
        accesoPermitido = True
    else:
        bottle.response.set_cookie("account", 'vacio')
    return accesoPermitido

@bottle.route('/static/<filename:path>') 
def static(filename): 
    return bottle.static_file(filename, root='static/')

@bottle.post('/seleccionar')
def seleccionarContactos():
    '''Metodo POST capturar las variables  que vienen del FORM elegir-contactos 
    y procesarlas para luego mostrarla en los controles text de la vista 
    seleccionados en el ComboBox HTML'''

    server = pymongo.MongoClient('localhost', 27017)
    baseDatos = server.pyloroweb    
    coleccionContactos = baseDatos.contactos

    #Busca el objetoId del usuario en la base de datos mongodb
    usuario = bottle.request.get_cookie("account")
    print(usuario)
    objetoUsuarioId = buscarUsuarioId(usuario)

    #Capturar todas las variables que vienen del <FORM elegir-comtactos/>
    listaDevuelta = bottle.request.forms.getall('elegir-contactos')
    listaDevuelta2 = bottle.request.forms.getall('elegir-listas')

    #Busca en la Base de datos el nombre y el telefono los contactos seleccionados en el ComboBox
    contactosElegidos = ['{0}<{1}>'.format(f['nombre'], f['telefonos'])\
            for f in coleccionContactos.find({'nombre':{'$in':listaDevuelta}, "usuario_id":objetoUsuarioId})]
    listasElegidas = listaDevuelta2

    #Aqui se buscan los contactos y las listas que pertecen al usuario que inico sesion para mostrarlos en los combobox
    nombresMostrar, listasMostrar = buscarContactosListas(objetoUsuarioId)
    
    textContactos = ','.join(contactosElegidos)
    textListas = ','.join(listasElegidas)

    return bottle.template('pyloro_sms_multiple.html', text1=textContactos, text2=textListas, comboBoxContactos=nombresMostrar, comboBoxListas=listasMostrar)

@bottle.route('/llamados')
def llamados():
    return bottle.template('llamados.html')

@bottle.route('/actualizar')
def llamados():
    return bottle.template('actualizar.html')

@bottle.route('/salir')
def salir():
    usuario = 'vacio'
    bottle.response.set_cookie("account", usuario)
    username = bottle.request.get_cookie("account")
    print('usuario',username)
    return bottle.template('index.tpl')

@bottle.route('/')
def index():
    usuario = 'vacio'
    bottle.response.set_cookie("account", usuario)

    username = bottle.request.get_cookie("account")
    print('usuario',username)
    return bottle.template('index.tpl')

@bottle.post('/')
def login():
    ''' Metodo para el inicio de Sesion en pyLoroWeb'''
    #global usuario
    #global clave
   
    usuario = ''
    clave = ''
    buscar = False

    usuario = bottle.request.forms.get('usu_form')
    clave = bottle.request.forms.get('pass_form')

    buscar = validaLogin(usuario, clave)
    
    if buscar:        
        objetoUsuarioId = buscarUsuarioId(usuario)
        nombresMostrar, listasMostrar = buscarContactosListas(objetoUsuarioId)
        return bottle.template('pyloro_sms_multiple.html', comboBoxContactos=nombresMostrar, comboBoxListas=listasMostrar)
    else:
        cabecera = 'Lo Siento...!'
        msg = 'El usuario o la clave es invalida'
        return bottle.template('mensaje_login', {'cabecera':cabecera, 'mensaje':msg})

@bottle.route('/smsenviar')
def smsEnviar():
    usuario = bottle.request.get_cookie("account")
    if usuario != 'vacio':
        print('usuario',usuario)
        objetoUsuarioId = buscarUsuarioId(usuario)
        nombresMostrar, listasMostrar = buscarContactosListas(objetoUsuarioId)
        return bottle.template('pyloro_sms_multiple.html', comboBoxContactos=nombresMostrar, comboBoxListas=listasMostrar)
    else:
        cabecera = 'Lo Siento ...!'
        msg = 'Ud. no ha iniciado sesion en el servidor'
        return bottle.template('mensaje_login', {'cabecera':cabecera, 'mensaje':msg})

@bottle.post('/smsenviar')
def smsEnviar():
    ''' Metodo que captura lo ingresado en el form de envio de SMS
    y lo envia al servidor ZMQ con la Clase enviar '''

    contactos = bottle.request.forms.get('contactos')
    listas = bottle.request.forms.get('listas')
    numeros = bottle.request.forms.get('numeros')
    mensaje = bottle.request.forms.get('mensaje')
    
    listasNumeros = componerContactosListas(contactos, listas) + numeros.split(',')

    usuario = bottle.request.get_cookie("account")

    if usuario == 'vacio':
        cabecera = 'Lo Siento ...!'
        msg = 'Ud. no ha iniciado sesion en el servidor'
        return bottle.template('mensaje_login', {'cabecera':cabecera, 'mensaje':msg})
    else:
        if not ''.join(listasNumeros) or not mensaje.strip():
            cabecera = 'Lo siento ...!'
            msg = 'Mensaje, Grupos o Numeros de telefonos estan vacios'
        else:
            for numero in listasNumeros:
                if validaSms(numero, mensaje.strip()):
                    devuelve = app.enviar(numero, mensaje)
                    if devuelve:
                        cabecera = 'Felicidades ...'
                        msg = 'Mensaje enviado con exito'.format(numero)
                    else:
                        cabecera = 'Lo Siento ...!'
                        msg = 'No se pudo enviar el SMS al numero:{0}'.format(numero)
                        
    return bottle.template('mensaje_exito', {'cabecera':cabecera, 'mensaje':msg, 'pagina':'/smsenviar'})

@bottle.route('/contactoNuevo')
def contactos():
    usuario = bottle.request.get_cookie("account")
    if usuario != 'vacio':
        grupos = buscarGrupos()
        return bottle.template('contactos',{'comboBoxGrupos':grupos})
    else:
        cabecera = 'Lo Siento ...!'
        msg = 'Ud. no ha iniciado sesion en el servidor'
        return bottle.template('mensaje_login', {'cabecera':cabecera, 'mensaje':msg})

@bottle.post('/contactoNuevo')
def contactoGuardar():
    '''Metodo que permite guardar un contacto desde el metodo post del form '''
    
    usuario = bottle.request.get_cookie("account")

    server = pymongo.MongoClient('localhost', 27017)
    baseDatos = server.pyloroweb    
    coleccionListas = baseDatos.listas
    coleccionContactos = baseDatos.contactos

    #Capturo desde el form html los campos 
    #idDevuelto = bottle.request.forms.get('id')
    nombreDevuelto = bottle.request.forms.get('nombres')
    apellidoDevuelto = bottle.request.forms.get('apellidos')
    telefonoDevuelto = bottle.request.forms.get('telefono')
    emailDevuelto = bottle.request.forms.get('email')
    tuiterDevuelto = bottle.request.forms.get('tuiter')
    gruposDevuelto = bottle.request.forms.get('grupos').split(',')
    
    #Busca en mongodb el objetoId del usuario que inicio sesion
    objetoUsuarioId = buscarUsuarioId(usuario)

    #Busca en la base de datos "listas" los objetosId() de las listas que fueron selecioandas en el combobox
    #del html solo para el usuario que inicio sesion
    devolverGruposID = [f['_id'] for f in coleccionListas.find({'nombre_lista':{'$in':gruposDevuelto}, "usuario_id":objetoUsuarioId})]

    #Armo el documento o regisrtos que se insertara en la base de datos mongodb
    documento = {'usuario_id':objetoUsuarioId, 'nombre':nombreDevuelto, 'apellido':apellidoDevuelto,
            'telefonos':telefonoDevuelto, 'email':emailDevuelto, 'twitter':tuiterDevuelto, 'listas_id':devolverGruposID}
    
    #Inserto el documento en mongodb
    try:
        coleccionContactos.insert(documento)
        print(documento)
        cabecera = 'Felicidades ...'
        msg = 'Contacto Guardado con exito'
    except:
        cabecera = 'Lo Siento ...'
        msg = 'Ocurrio un error al Guardar'
    return bottle.template('mensaje_exito', {'cabecera':cabecera, 'mensaje':msg, 'pagina':'/contactoNuevo'})

@bottle.route('/grupoNuevo')
def grupoNuevo():
    
    usuario = bottle.request.get_cookie("account")
    if usuario != 'vacio':
        return bottle.template('grupos')
    else:
        cabecera = 'Lo Siento ...!'
        msg = 'Ud. no ha iniciado sesion en el servidor'
        return bottle.template('mensaje_login', {'cabecera':cabecera, 'mensaje':msg})


@bottle.post('/grupoNuevo')
def grupoGuardar():
    '''Metodo que permite guardar un grupo desde el metodo post del form '''
    
    usuario = bottle.request.get_cookie("account")

    server = pymongo.MongoClient('localhost', 27017)
    baseDatos = server.pyloroweb    
    coleccionListas = baseDatos.listas

    #Capturo desde el form html los campos 
    #idDevuelto = bottle.request.forms.get('id')
    nombreDevuelto = bottle.request.forms.get('nombre')
    descripcionDevuelto = bottle.request.forms.get('descripcion')
    
    #Busca en mongodb el objetoId del usuario que inicio sesion
    objetoUsuarioId = buscarUsuarioId(usuario)

    #Armo el documento o regisrtos que se insertara en la base de datos mongodb
    documento = {'usuario_id':objetoUsuarioId, 'nombre_lista':nombreDevuelto, 'descripcion':descripcionDevuelto}
    
    #Inserto el documento en mongodb
    try:
        coleccionListas.insert(documento)
        cabecera = 'Felicidades ...'
        msg = 'Grupo Guardado con exito'
    except:
        cabecera = 'Lo Siento ...'
        msg = 'Ocurrio un error al Guardar'
    return bottle.template('mensaje_exito', {'cabecera':cabecera, 'mensaje':msg, 'pagina':'/grupoNuevo'})

@bottle.get('/registro')
def registro():
    ''' **Metodo que permite registrar una cuenta en el Sistema pyLoro**
    Se captura el usuario que esta creando la cuenta, si no hay usuario es porque se esta creando desde la
    pantalla de inicio lo cual significa que este usuario sera una especie de root y no tiene ningun
    usuario padre, en cambio si tiene un usuario padre debe heredar los planes del usuario padre '''

    cliente = pymongo.MongoClient('localhost', 27017)
    baseDatos = cliente.pyloroweb
    coleccionUsuarios = baseDatos.usuarios
    
    usuario = bottle.request.get_cookie("account")

    try:
        #Buscar el plan del usuario padre y devolverlo a la plantilla
        #usuario_padre_id = buscarUsuarioId(usuario)
        usuarioBuscar = coleccionUsuarios.find({'usuario':usuario})
        if usuarioBuscar.count()>0:
            usuarioEncontrado = usuarioBuscar[0]
            #usu = usuarioEncontrado['usuario']
            nom = usuarioEncontrado['nombres']
            #telf = usuarioEncontrado['telefono']
            #email = usuarioEncontrado['email']
            usu_padre_id = usuarioEncontrado['usuario_padre_id']

            usuarioActivo = 'checked="checked"'
            plan = 'El del Padre:{0}'.format(nom)
        else:
            usu_padre_id = ''
            usuarioActivo = ''
            plan = ''
    except:
        #como no tiene usuario padre se le da la opcion que el seleccione el plan
        #pero el usuario debe estar inactivo hasta que no sea apobado por mi
        usu_padre_id = ''
        usuarioActivo = ''
        plan = ''
    return bottle.template('registro', {'estructuraOrganizativa':usu_padre_id, 'usuarioActivo':usuarioActivo, 'planp':plan})

@bottle.post('/registro')
def registroGuardar():
    '''Metodo que permite registrar una cuenta en el Sistema pyLoro'''

    cliente = pymongo.MongoClient('localhost', 27017)
    baseDatos = cliente.pyloroweb
    coleccionUsuarios = baseDatos.usuarios

    #id = bottle.request.forms.get('id')
    usuario = bottle.request.forms.get('usuario')

    clave = bottle.request.forms.get('clave')
    nombres = bottle.request.forms.get('descripcion')
    ced_rif = bottle.request.forms.get('cedrif')
    fecha = datetime.datetime.now()
    direccion = bottle.request.forms.get('direccion')
    telefono = bottle.request.forms.get('telefono')
    email = bottle.request.forms.get('email')
    plan = bottle.request.forms.get('plan')
    usuario_padre_id = bottle.request.forms.get('estructura')
    activo = True if usuario_padre_id else False  # bottle.request.forms.get('activo')
    
    documento = {'usuario':usuario,
            'clave':clave,
            'nombres':nombres,
            'ced_rif':ced_rif,
            'fecha_creacion':fecha,
            'direccion':direccion,
            'telefono':telefono,
            'email':email,
            'plan':plan,
            'usuario_padre_id':usuario_padre_id,
            'activo':activo}
    
    existe = coleccionUsuarios.find({'usuario':usuario.lower()}).count()
    if not existe:
        try:
            #Si no existe el usuario Se agrega el usuario nuevo
            coleccionUsuarios.insert(documento)
            cabecera = 'Felicidades ...'
            msg = 'Registro realizado con exito' if usuario_padre_id else 'Registro realizado con Exito, en unos minutos su cuenta estara activa'
            if not usuario_padre_id:
                app.enviar('04263002966', 'El usuario {0} espera por aprobacion de creacion de cuenta en pyLoroWeb'.format(nombres))
                #Enviar email tambien
        except:
            cabecera = 'Lo Siento ...'
            msg = 'Ocurrio un error al Guardar'
    else:
        cabecera = 'Lo Siento ...'
        msg = 'Usuario {0} Ya esta registrado'.format(usuario)

    return bottle.template('mensaje_exito', {'cabecera':cabecera, 'mensaje':msg, 'pagina':'/registro'})

@bottle.get('/grid')
def grid():
    grid = [('Carlos', 'Garcia', 'Diaz'), ('Nairesther', 'Gomez', 'Villa'), ('Carla', 'Garcia', 'Gomez'), ('Paola', 'Garcia', 'Sanchez')]
    return bottle.template('grid', {'grid':grid})

def componerContactosListas(contactos, listas):
    '''Obtener solo los numeros de telefonos de las selecciones
    hechas en l combobox del html'''
    
    server = pymongo.MongoClient('localhost', 27017)
    baseDatos = server.pyloroweb    
    coleccionContactos = baseDatos.contactos
    coleccionListas = baseDatos.listas

    recvContactos = contactos.split(',')
    recvListas = listas.split(',')

    print('listas recv', recvListas)

    #se toma solo el numero de recvContactos ya que este devuelve una lista con nombre y numeros 'Carlos<04263002966>'
    #patron = r'[0-9]{11}'
    #devolverContactos = re.findall(patron, recvContactos)

    #Busca en mongodb el objetoId del usuario que inicio sesion
    usuario = bottle.request.get_cookie("account")
    objetoUsuarioId = buscarUsuarioId(usuario)

    devolverContactos = [f['telefonos'] for f in coleccionContactos.find({'nombre':{'$in':recvContactos}, "usuario_id":objetoUsuarioId})]


    ''' Busca en la base de datos "listas" los objetosId() de las listas 
    que fueron selecioandas en el comboboxdel html'''
    devolverListasID = [f['_id'] for f in coleccionListas.find({'nombre_lista':{'$in':recvListas}, "usuario_id":objetoUsuarioId})]
    print('listas id', devolverListasID)
    
    '''Buscos en la tabla "contactos" los objetosId() de las listas devueltas anteriormente y tomo solo los 
    contactos que pertencen a esas listas'''
    devolverListas = [f['telefonos'] for f in coleccionContactos.find({'listas_id':{'$in':devolverListasID}, "usuario_id":objetoUsuarioId})]
    print('telefonos', devolverListas)

    numeros = devolverContactos + devolverListas
    print('numeros', numeros)
    return numeros 

def validaSms(num, msg):
    devuelve = True
    if not num:
        devuelve = False
    elif not msg:
        devuelve = False
    elif len(num) !=11:
        devuelve = False
    elif num[:4] not in ['0426', '0416', '0414', '0424', '0412']:
        devuelve = False
    return devuelve

bottle.debug(True)
bottle.run(host='0.0.0.0', port=8085)

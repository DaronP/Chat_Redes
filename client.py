'''
Universidad del Valle de Guatemala
Redes
Jorge Andres Perez Barrios
Carnet: 16362
'''


from slixmpp import ClientXMPP, clientxmpp
import sys
import logging
import getpass
import asyncio
import slixmpp
from slixmpp.exceptions import IqError, IqTimeout
from xml.etree import ElementTree as ET



if sys.platform == 'win32':
	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

#Clase para registro de usuarios
class SignUp(slixmpp.ClientXMPP):

	def __init__(self, jid, password):
		ClientXMPP.__init__(self, jid, password)

		self.add_event_handler("session_start", self.start)
		self.add_event_handler("register", self.register)

	async def start(self, event):
		self.send_presence()
		await self.get_roster()

		self.disconnect()

	async def register(self, iq):
		resp = self.Iq()
		resp['type'] = 'set'
		resp['register']['username'] = self.boundjid.user
		resp['register']['password'] = self.password
		try:
			await resp.send()
			print("Account created for %s!" % self.boundjid)
			self.disconnect()

		except IqError as e:
			print("Could not register account: %s" %
					e.iq['error']['text'])
			self.disconnect()
			
		except IqTimeout:
			print("No response from server.")
			self.disconnect()
		self.disconnect()
		sys.exit()

'''
Clase de cliente
Contiene las funcionalidades para poder utilizar el chat
-Ver usuarios
-Agregar usuarios
-Mostrar detalles de un contacto
-Mandar mensaje a un usuario
-Ingresar a un room
-Mandar mensaje a un room
-Cambiar estado
-Desconectarse
-Eliminar cuenta
'''

class Client(ClientXMPP):
	#Constructor
	def __init__(self, jid, password):
		ClientXMPP.__init__(self, jid, password)
		self.jid = jid
		self.password = password

		self.add_event_handler('session_start', self.session_start)
		self.add_event_handler('receive_message', self.receive)
		self.add_event_handler('muc_receive', self.muc_message)
		self.add_event_handler('message', self.message)
		self.add_event_handler('greeting', self.muc_greeting)
		self.add_event_handler('unregister', self.delete_acc)

		self.register_plugin('xep_0030') # Service Discovery		
		self.register_plugin('xep_0045') # Multi-User Chat
		self.register_plugin('xep_0004')
		self.register_plugin('xep_0060')
		self.register_plugin('xep_0199') # Ping

		self.received = set()
		self.presences_received = asyncio.Event()

	#Funcion que recibe mensajes, tanto personales como grupales
	def receive(self, msg):
		if msg['type'] == 'chat' or msg['type'] == 'normal':
			print("***********Mensaje Recibido**************")
			print("De: %(from)s \n %(body)s" %(msg))
			print("*****************************************")
			msg.reply("Mensaje %(body)s enviado correctamente" % msg['body'])

		if msg['type'] == 'groupchat':
			print("***********Mensaje grupal Recibido**************")
			print("De: %(from)s \n %(body)s" %(msg))
			print("************************************************")
			msg.reply("Mensaje %(body)s enviado correctamente" % msg['body'])

	#Funcion de confirmacion de envio de mensajes
	def message(self, msg):
		if msg['type'] in ('chat', 'normal'):
			msg.reply("Thanks for sending\n%(body)s" % msg).send()

	#Funcion de saludo al entrar a un room
	def muc_greeting(self, presence):
		if presence['muc']['nick'] != self.nick:
			self.send_message(mto=presence['from'].bare, mbody="Bienvenido, %s %s" % (presence['muc']['role'], presence['muc']['nick']), mtype='groupchat')

	#Funcion para enviar mensajes grupales
	def muc_message(self, room, msg):
		try:
			self.send_message(mto=room, mbody=msg, mtype='groupchat')
		except IqError as e:
			print("Error al mandar mensaje " ,e)
	
	#Funcion para eliminar una cuenta
	def delete_acc(self):
		iq_stanza = self.make_iq_set(ito='alumchat.xyz', ifrom=self.boundjid.user)
		item = ET.fromstring("<iq type='set' id='unreg1'> \
								<query xmlns='jabber:iq:register'> \
									<remove/> \
								</query> \
								</iq>")
		iq_stanza.append(item)
		res = iq_stanza.send()
		if res['type'] == 'result':
			print("Usuario removido...")
			sys.exit()

	#Inicio: menu asincrono con asyncio
	async def session_start(self, event):
		self.send_presence()
		await self.get_roster()
		
		chat = True
		while chat:
			opcion = input("Menu:\n1. Ver todos los usuarios y sus estados\n2. Agregar usuarios\n3. Mostrar detalles de un contacto\n4. Mandar mensaje a un usuario\n5. Ingresar a un room\n6. Mandar mensaje a un room\n7. Cambiar estado\n8. Desconectarse\n9. Eliminar cuenta\n")
			
			#1. Ver todos los usuarios y sus estados
			if opcion == "1":
				
				print('Waiting for presence updates...\n')
				await asyncio.sleep(10)
				print('Roster for %s' % self.boundjid.bare)
				for i in self.roster:
					for r in self.roster[i]:
						print(r.split('@')[0])
						for s in self.client_roster.presence(r):
							print("    status: ", self.client_roster.presence(r)[s]['status'])

			#2. Agregar usuarios
			if opcion == "2":
				usr = input("Ingrese usuario ")
				usr = usr + "@alumchat.xyz"
				xmpp.send_presence_subscription(pto=usr)
				print("Usuario agregado")

			#3. Mostrar detalles de un contacto
			if opcion == "3":
				usr = input("Ingrese el usuario ")
				usr = usr + "@alumchat.xyz"
				print("    status: ", self.client_roster.presence(r)[s]['status'])
				print(self.client_roster.presence(usr))
				y = self.client_roster
				print(y[usr])
				continue
			
			#4. Mandar mensaje a un usuario
			if opcion == "4":
				para = input("Ingrese el usuario ")
				para = para + "@alumchat.xyz"
				msg = input("Ingrese el mensaje ")

				try:
					self.send_message(mto=para, mbody=msg, mtype='chat')
					print("Mensaje enviado")
				except:
					print("No se ha podido mandar el mensaje")
				
				continue
			
			#5. Ingresar a un room
			if opcion == "5":
				nick = input("Ingrese su nick ")
				room = input("Ingrese el nombre del room ")
				self.room = room + '@muc.alumchat.xyz'
				res = self.get_roster(self.room)
				self.nick = nick
				
				await self.get_roster()
				self.send_presence()
				
				self.plugin['xep_0045'].join_muc(self.room, self.nick)
				self.add_event_handler("muc::%s::got_online" % self.room,self.muc_greeting)
				print("Grupo añadido con exito")
				continue

			#6. Mandar mensaje a un room
			if opcion == "6":
				room = input("Ingrese el room ")
				room = room + "@muc.alumchat.xyz"
				msg = input("Ingrese el mensaje ")
				self.muc_message(room, msg)
				continue
			
			#7. Cambiar estado
			if opcion == "7":
				show = input("Estado: chat, away, xa, dnd...")
				status = input("Ingrese su estado ")
				self.send_presence(pshow=show, pstatus=status)
				print("Correcto.")
				continue
			
			#8. Desconectarse
			if opcion == "8":
				self.disconnect()
				sys.exit()
			
			#9. Eliminar cuenta
			if opcion == "9":
				self.delete_acc()
				sys.exit()

			else:
				print("Seleccion incorrecta")

if __name__ == '__main__':

	run = True

	while run:
		opcion = input("1. Ingresar \n2. Registrarse \n3. Salir \n")
		if opcion == "1" or opcion == 1:
			jid = input("Username: ")
			jid = jid + '@alumchat.xyz'
			password = getpass.getpass("Password: ")
				
			xmpp = Client(jid, password)
				
			if xmpp.connect() == None:
				xmpp.process()
				
			else:
				print("Error al conectarse")
		
		if opcion == "2" or opcion == 2:
			jid = input("Username: ")
			jid = jid + '@alumchat.xyz'
				
			password = getpass.getpass("Password: ")
			password2 = getpass.getpass("Confirm password: ")

			if password == password2:
			
				xmpp = SignUp(jid, password)
				xmpp.register_plugin('xep_0030') # Service Discovery
				xmpp.register_plugin('xep_0004') # Data forms
				xmpp.register_plugin('xep_0066') # Out-of-band Data
				xmpp.register_plugin('xep_0077') # In-band Registration
				xmpp['xep_0077'].force_registration = True
				if xmpp.connect() == None:
					xmpp.process()
					print("Success")
			else: 
				print("Las contraseñas no coinciden...")
		if opcion == 3 or opcion == "3":
			run = False


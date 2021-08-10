from slixmpp import ClientXMPP, clientxmpp
import sys
import logging
import getpass
import asyncio
import slixmpp
from slixmpp.exceptions import IqError, IqTimeout


if sys.platform == 'win32':
	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class SignUp(slixmpp.ClientXMPP):

	def __init__(self, jid, password):
		slixmpp.ClientXMPP.__init__(self, jid, password)

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

		except IqError as e:
			print("Could not register account: %s" %
					e.iq['error']['text'])
			self.disconnect()
			
		except IqTimeout:
			print("No response from server.")
			self.disconnect()
		self.disconnect()


class Client(ClientXMPP):
	def __init__(self, jid, password):
		super().__init__(jid, password)
		self.jid = jid
		self.password = password

		self.register_plugin('xep_0030') # Service Discovery		
		self.register_plugin('xep_0045') # Multi-User Chat
		self.register_plugin('xep_0004')
		self.register_plugin('xep_0060')
		self.register_plugin('xep_0199') # Ping
		
		#self.recipient = recipient
		#self.msg = msg
		self.add_event_handler('session_start', self.session_start)
		self.add_event_handler('receive_message', self.receive)
		self.add_event_handler('message', self.message)

	def receive(self, msg):
		if msg['type'] == 'chat' or msg['type'] == 'normal':
			print("***********Mensaje Recibido**************")
			print("De: %(from)s \n %(body)s" %(msg))
			print("*****************************************")

	def message(self, msg):
		if msg['type'] in ('chat', 'normal'):
			msg.reply("Thanks for sending\n%(body)s" % msg).send()

	
	async def session_start(self, event):
		self.send_presence()
		await self.get_roster()
		
		chat = True
		while chat:
			opcion = input("Holis")
			if opcion == "1":

				self.send_presence(pstatus='available')
				#se realiza una actualizacion de los presence
				print('Waiting for presence updates...\n')
				await asyncio.sleep(10)
				#aqui se procura el desplegar el roster de contatos en el server
				#consta de varios loops que muestran los distintos detalles de los usuarios
				print('Roster for %s' % self.boundjid.bare)
				for i in self.roster:
					for r in self.roster[i]:
						print(r.split('@')[0])
						for s in self.client_roster.presence(r):
							print("    status: ", self.client_roster.presence(r)[s]['status'])


			if opcion == "2":
				usr = input("Ingrese usuario ")
				usr = usr + "@alumchat.xyz"
				xmpp.send_presence_subscription(pto=usr)
				print("Usuario agregado")

			if opcion == "3":
				usr = input("Ingrese el usuario ")
				usr = usr + "@alumchat.xyz"
				print(self.client_roster.presence(usr))
				y = self.client_roster
				print(y[usr])
			
			if opcion == "4":
				para = input("Ingrese el usuario ")
				para = para + "@alumchat.xyz"
				msg = input("Ingrese el mensaje ")

				try:
					self.send_message(mto=para, mbody=msg, mtype='chat')
					print("Mensaje enviado")
				except:
					print("No se ha podido mandar el mensaje")
		#self.send_message(mto=self.recipient, mbody=self.msg)

if __name__ == '__main__':

	connection = False
	

	run = True

	while run:
		opcion = input("1. Ingresar \n2. Registrarse \n3. Salir \n")
		if opcion == "1" or opcion == 1:
			jid = input("Username: ")
			jid = jid + '@alumchat.xyz'
			password = input("Password: ")
				
			xmpp = Client(jid, password)
				
			if xmpp.connect() == None:
				f = xmpp.client_roster
				xmpp.process()
				
			else:
				print("Error al conectarse")
		
		if opcion == "2" or opcion == 2:
			jid = input("Username: ")
			jid = jid + '@alumchat.xyz'
				
			password = getpass.getpass("Password: ")
			
			xmpp = SignUp(jid, password)
			xmpp.register_plugin('xep_0030') # Service Discovery
			xmpp.register_plugin('xep_0004') # Data forms
			xmpp.register_plugin('xep_0066') # Out-of-band Data
			xmpp.register_plugin('xep_0077') # In-band Registration
			xmpp['xep_0077'].force_registration = True
			if xmpp.connect() == None:
				xmpp.process()
				print("Success")
		if opcion == 3 or opcion == "3":
			run = False


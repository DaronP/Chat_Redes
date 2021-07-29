import sys
import asyncio
import logging
import getpass
from argparse import ArgumentParser
import slixmpp


from slixmpp import ClientXMPP


class EchoBot(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)
        super().__init__(jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

        # If you wanted more functionality, here's how to register plugins:
        # self.register_plugin('xep_0030') # Service Discovery
        # self.register_plugin('xep_0199') # XMPP Ping

        # Here's how to access plugins once you've registered them:
        # self['xep_0030'].add_feature('echo_demo')

    async def session_start(self, event):
        self.send_presence()
        await self.get_roster()

        # Most get_*/set_* methods from plugins use Iq stanzas, which
        # are sent asynchronously. You can almost always provide a
        # callback that will be executed when the reply is received.

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending:\n%s" % msg['body']).send()


if __name__ == '__main__':
    # Setup the command line arguments.
    parser = ArgumentParser(description=EchoBot.__doc__)

    # Output verbosity options.
    parser.add_argument("-q", "--quiet", help="set logging to ERROR", action="store_const", dest="loglevel",
    const=logging.ERROR, default=logging.INFO)

    parser.add_argument("-d", "--debug", help="set logging to DEBUG", action="store_const", dest="loglevel",
    const=logging.DEBUG, default=logging.INFO)

    # JID and password options.
    parser.add_argument("-j", "--jid", dest="jid", help="JID to use")

    parser.add_argument("-p", "--password", dest="password", help="password to use")

    args = parser.parse_args()

    if args.jid is None:
        args.jid = input("Username: ")
        args.jid = args.jid + '@openfire.alumchat.xyz'

    if args.password is None:
        args.password = input("Password: ")

    logging.basicConfig(level=args.loglevel, format='%(levelname)-8s %(message)s')

    xmpp = EchoBot(args.jid, args.password)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0199') # Ping

    xmpp.connect()
    xmpp.process(forever=True)


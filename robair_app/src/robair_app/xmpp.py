import rospy
from sleekxmpp import ClientXMPP
# import cPickle
import inspect
import traceback
from robair_common.logger import LOGGER
from robair_common.utils import parse_args, retry


class RemoteXMPPException(Exception):
    '''Exception that happens when the remote method call failled'''
    def __str__(self):
        return self.__doc__


def remote(*args, **kwargs):
    """Decorator for remote xmpp functions"""

    def decorate(func, name=None, threaded=False):
        setattr(func, '_xmpp_remote', True)
        return func

    if len(args):
        return decorate(args[0], **kwargs)
    else:
        return lambda func: decorate(func, **kwargs)


class RemoteXMPPProxy(object):
    """ RemoteXMPPProxy """
    def __init__(self, client, remote_jid):
        self.client = client
        self.remote_jid = remote_jid

        @retry(tries=3, delay=1)
        def ping():
            LOGGER.debug("Try to ping %s" % self.remote_jid)
            result = self.client['xep_0199'].send_ping(self.remote_jid,
                                                       timeout=10,
                                                       errorfalse=True)
            LOGGER.debug("%s" % result)
            if not result:
                LOGGER.info("Couldn't ping %s" % self.remote_jid)
                return result
            else:
                return True

        if not ping():
            message = "remote XMPP agent (%s) is unavailable" % self.remote_jid
            raise RemoteXMPPException(message)

    def __rpc(self, name, *args, **kwargs):
        print("remote_method : %s %s" % (args, kwargs))

    def __getattr__(self, name):
        return lambda *args, **kwargs: self.__rpc(name, args, kwargs)


class BotXMPP(ClientXMPP):
    MSG_ERROR_OCCURRED = 'Sorry for your inconvenience. '\
                         'An unexpected error occurred.'
    MSG_UNKNOWN_COMMAND = 'Unknown command: %s". \n'

    def __init__(self, jid, password, node_name):
        super(BotXMPP, self).__init__(jid, password)
        rospy.init_node(node_name)
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message_handler)
        self.load_plugin()

        self.remote_cmds = {}
        for name, value in inspect.getmembers(self, inspect.ismethod):
            if getattr(value, '_xmpp_remote', False):
                name = getattr(value, '__name__')
                LOGGER.info('Registered remote method: %s' % name)
                self.remote_cmds[name] = value

        self.connect()
        self.process(block=False)

    def get_proxy(self, jid):
        return RemoteXMPPProxy(self, jid)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def execute_and_send(self, func, msg, args, kwargs):
        """ Execute command and reply with the result. """
        def task(func, args, kwargs):
            try:
                result = func(*args, **kwargs)
                msg.reply("%s" % result).send()
            except Exception as e:
                exception = traceback.format_exc(e)
                LOGGER.exception('An error happened while processing '
                                 'a message ("%s") from %s: %s"' %
                                 (msg['body'], msg['from'], exception))
                msg.reply("%s\n" % (self.MSG_ERROR_OCCURRED)).send()

        task(func, args, kwargs)

    def message_handler(self, msg):
        LOGGER.info("%s read: %s" % (self.__class__.__name__, msg['body']))
        if (msg['type'] not in ('chat', 'normal')
                or msg['body'] == ''):
            return
        msg_parts = msg['body'].split(' ')
        cmd, args = msg_parts[0], msg_parts[1:] if len(msg_parts) > 1 else []
        args, kwargs = parse_args(args)
        LOGGER.debug("cmd : %s :: args : %s :: kwargs : %s" %
                     (cmd, args, kwargs))

        if cmd in self.remote_cmds:
            func = self.remote_cmds[cmd]
            self.execute_and_send(func, msg, args, kwargs)

    def send_message(self, dest, mbody):
        super(BotXMPP, self).send_message(mto=dest, mbody=mbody, mtype='chat')

    def load_plugin(self):
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0004')  # Data Forms
        self.register_plugin('xep_0060')  # PubSub
        self.register_plugin('xep_0199')  # XMPP Ping
        self.auto_reconnect = True

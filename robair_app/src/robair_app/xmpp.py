import rospy
from sleekxmpp import ClientXMPP
# import cPickle
import inspect
import traceback
from robair_common.logger import LOGGER
from robair_common.utils import parse_args


def botcmd(*args, **kwargs):
    """Decorator for bot command functions"""

    def decorate(func, name=None, threaded=False):
        setattr(func, '_command', True)
        setattr(func, '_command_name', name or func.__name__)
        setattr(func, '_threaded', threaded)  # Experimental!
        return func

    if len(args):
        return decorate(args[0], **kwargs)
    else:
        return lambda func: decorate(func, **kwargs)


class BotXMPP(ClientXMPP):
    MSG_ERROR_OCCURRED = 'Sorry for your inconvenience. '\
                         'An unexpected error occurred.'
    MSG_UNKNOWN_COMMAND = 'Unknown command: %s". \n'

    def __init__(self, jid, password, node_name, num_thread=2):
        super(BotXMPP, self).__init__(jid, password)
        rospy.init_node(node_name)
        self.add_event_handler("session_start", self._session_start)
        self.add_event_handler("message", self._message_handler)
        self._load_plugin()

        self.commands = {}
        for name, value in inspect.getmembers(self, inspect.ismethod):
            if getattr(value, '_command', False):
                name = getattr(value, '_command_name')
                LOGGER.info('Registered command: %s' % name)
                self.commands[name] = value

    def _session_start(self, event):
        self.send_presence()
        self.get_roster()

    def _execute_and_send(self, func, msg, args, kwargs):
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

        if func._threaded:
            self.threads_pool.add_task(task, args, kwargs)
        else:
            task(func, args, kwargs)

    def _message_handler(self, msg):
        LOGGER.info("%s read: %s" % (self.__class__.__name__, msg['body']))
        if (msg['type'] not in ('chat', 'normal')
                or msg['body'] == ''):
            return
        msg_parts = msg['body'].split(' ')
        cmd, args = msg_parts[0], msg_parts[1:] if len(msg_parts) > 1 else []
        args, kwargs = parse_args(args)
        LOGGER.debug("cmd : %s :: args : %s :: kwargs : %s" %
                     (cmd, args, kwargs))

        if cmd in self.commands:
            func = self.commands[cmd]
            self._execute_and_send(func, msg, args, kwargs)
        else:
            msg.reply(self.MSG_UNKNOWN_COMMAND % cmd).send()

    def send_message(self, dest, mbody):
        super(BotXMPP, self).send_message(mto=dest, mbody=mbody, mtype='chat')

    def _load_plugin(self):
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0004')  # Data Forms
        self.register_plugin('xep_0060')  # PubSub
        self.register_plugin('xep_0199')  # XMPP Ping
        self.auto_reconnect = True

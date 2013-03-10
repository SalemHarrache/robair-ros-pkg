import logging
import rospy
from sleekxmpp import ClientXMPP
import cPickle
import thread
import inspect
from robair_msgs.msg import Command


def botcmd(*args, **kwargs):
    """Decorator for bot command functions"""

    def decorate(func, name=None, thread=False):
        setattr(func, '_jabberbot_command', True)
        setattr(func, '_jabberbot_command_name', name or func.__name__)
        setattr(func, '_jabberbot_command_thread', thread)  # Experimental!
        return func

    if len(args):
        return decorate(args[0], **kwargs)
    else:
        return lambda func: decorate(func, **kwargs)


class BotXMPP(ClientXMPP):
    MSG_ERROR_OCCURRED = 'Sorry for your inconvenience. '\
                         'An unexpected error occurred.'
    MSG_UNKNOWN_COMMAND = 'Unknown command: %s". \n'\
                          'Type help for available commands.'

    def __init__(self, jid, password, node_name):
        super(BotXMPP, self).__init__(jid, password)
        rospy.init_node(node_name)
        self.log = logging.getLogger(__name__)
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message_handler)
        self.load_plugin()

        self.commands = {}
        for name, value in inspect.getmembers(self, inspect.ismethod):
            if getattr(value, '_jabberbot_command', False):
                name = getattr(value, '_jabberbot_command_name')
                self.log.info('Registered command: %s' % name)
                self.commands[self.__command_prefix + name] = value

        logging.basicConfig()
        # import pdb; pdb.set_trace()

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def message_handler(self, msg):
        LOGGER.debug("msg['type'] = %s" % msg['type'])
        if (msg['type'] not in ('chat', 'normal')
                or msg['body'] == ''):
            return
        msg_parts = msg['body'].split(' ')
        cmd, args = msg_parts[0], msg_parts[-1:] if len(msg_parts) > 1 else []
        LOGGER.debug("cmd : %s :: args : %s" % (cmd, args))
        if cmd in self.commands:
            def execute_and_send():
                try:
                    msg.reply(self.commands[cmd](*args)).send()
                except Exception:
                    msg.reply(self.MSG_ERROR_OCCURRED).send()

            # Experimental!
            # if command should be executed in a seperate thread do it
            if self.commands[cmd]._jabberbot_command_thread:
                thread.start_new_thread(execute_and_send, ())
            else:
                execute_and_send()
        else:
            pass
            # # In private chat, it's okay for the bot to always respond.
            # # In group chat, the bot should silently ignore commands it
            # # doesn't understand or aren't handled by unknown_command().
            # if type == 'groupchat':
            #     default_reply = None
            # else:
            #     default_reply = self.MSG_UNKNOWN_COMMAND % {
            #         'command': cmd,
            #         'helpcommand': 'help',
            #     }
            # reply = self.unknown_command(mess, cmd, args)
            # if reply is None:
            #     reply = default_reply
            # if reply:
            #     self.send_simple_reply(mess, reply)

        # print(msg['body'])
        # topic_data = cPickle.loads(msg)
        # self.pub = rospy.Publisher(topic_data.topic, topic_data.data)

    def send_message(self, dest, mbody):
        super(BotXMPP, self).send_message(mto=dest, mbody=mbody, mtype='chat')

    def load_plugin(self):
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0004')  # Data Forms
        self.register_plugin('xep_0060')  # PubSub
        self.register_plugin('xep_0199')  # XMPP Ping
        self.auto_reconnect = True


class RobBot(BotXMPP):
    def __init__(self, node_name):
        jid = rospy.get_param('robot_jabber_id')
        password = rospy.get_param('robot_jabber_password')
        super(RobBot, self).__init__(jid, password, node_name)


class ClientBot(BotXMPP):
    def __init__(self, node_name):
        jid = rospy.get_param('tv_jabber_id')
        password = rospy.get_param('tv_jabber_password')
        self.robot_jid = rospy.get_param('robot_jabber_id')
        super(ClientBot, self).__init__(jid, password, node_name)

        self.topic_name = "/cmd"
        rospy.Subscriber(self.topic_name, Command, self.callback)
        rospy.spin()

    def callback(self, data):
        rospy.loginfo("%s: I heard  speed %s - curve %s :D"
                      % (rospy.get_name(), data.speed, data.angle))
        topic_to_serialize = {"topic": self.topic_name, "data": data}
        msg = cPickle.dumps(topic_to_serialize)
        self.send_message(self.robot_jid, msg)

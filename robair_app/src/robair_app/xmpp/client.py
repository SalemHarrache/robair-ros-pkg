from Queue import Queue
import inspect
import sleekxmpp
import traceback

from robair_common.logger import LOGGER
from .rpc import RemoteXMPPProxy, RPCMessage, RPCRequest, RPCResponse,\
    RemoteXMPPException, RPCSession


class ClientXMPP(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        super(ClientXMPP, self).__init__(jid, password)
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message_handler)
        self.load_plugin()

        self.remote_cmds = {}
        for name, value in inspect.getmembers(self, inspect.ismethod):
            if getattr(value, '_xmpp_remote', False):
                if name not in self.remote_cmds:
                    name = getattr(value, '__name__')
                    LOGGER.info('Registered remote method: %s' % name)
                    self.remote_cmds[name] = value

        self.response_queue = Queue()
        self.connect()
        self.process(Block=False)

    def get_proxy(self, jid):
        return RemoteXMPPProxy(self, jid)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def current_rpc_session(self):
        """ Returns the current RPC session """
        session = getattr(self, "_current_rpc_session", None)
        if session is None:
            raise RuntimeError('working outside of RPC context')
        return session

    def message_handler(self, message):
        if (message['type'] not in ('chat', 'normal')
                or message['body'] == ''):
            return
        try:
            rpc_message = RPCMessage.loads(message['body'])
            LOGGER.info("read rpc_message: %s" % rpc_message)
            if isinstance(rpc_message, RPCRequest):
                LOGGER.debug("cmd : %s :: args : %s :: kwargs : %s" %
                             (rpc_message.proc_name, rpc_message.args,
                              rpc_message.kwargs))
                if rpc_message.proc_name in self.remote_cmds:
                    func = self.remote_cmds[rpc_message.proc_name]
                    try:
                        self._current_rpc_session = RPCSession(message,
                                                               rpc_message)
                        args, kwargs = rpc_message.args, rpc_message.kwargs
                        result = func(*args, **kwargs)
                        del self._current_rpc_session
                        rpc_response = RPCResponse(rpc_message.id, result)
                    except Exception as e:
                        m = traceback.format_exc(e)
                        LOGGER.debug("An exception occurred : %s" % m)
                        exception = RemoteXMPPException(e.message)
                        rpc_response = RPCResponse(rpc_message.id, m)
                    self.send_message(message['from'], rpc_response.dumps())
                self.request_handler(rpc_message, message)
            elif isinstance(rpc_message, RPCResponse):
                self.response_queue.put(rpc_message)
        except:
            pass

    def send_message(self, dest, mbody):
        super(ClientXMPP, self).send_message(mto=dest,
                                             mbody=mbody,
                                             mtype='chat')

    def load_plugin(self):
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0004')  # Data Forms
        self.register_plugin('xep_0060')  # PubSub
        self.register_plugin('xep_0199')  # XMPP Ping
        self.auto_reconnect = True

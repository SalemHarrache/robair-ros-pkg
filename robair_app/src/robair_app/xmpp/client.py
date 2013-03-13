import Queue
import inspect
import sleekxmpp

from robair_common.logger import LOGGER
from .rpc import RemoteXMPPProxy, RPCMessage, RPCRequest, RPCResponse, remote,\
    RemoteXMPPException


class ClientXMPP(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        super(ClientXMPP, self).__init__(jid, password)
        self.request_queue = Queue()
        self.response_queue = Queue()
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
        self.process()

    def process(self):
        # TODO: use additional worker for threaded rpc methods
        super(ClientXMPP, self).process(block=False)

    def get_proxy(self, jid):
        return RemoteXMPPProxy(self, jid)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def message_handler(self, msg):
        LOGGER.debug("%s read: %s" % (self.__class__.__name__, msg['body']))
        if (msg['type'] not in ('chat', 'normal')
                or msg['body'] == ''):
            return
        try:
            rpc_message = RPCMessage.loads(msg['body'])
            if isinstance(rpc_message, RPCRequest):
                self.request_handler(rpc_message)
                # self.request_queue.put(rpc_message)
            elif isinstance(rpc_message, RPCResponse()):
                self.response_queue.put(rpc_message)
        except:
            pass

    def request_handler(self, request):
        # TODO: Most be threaded !
        LOGGER.debug("cmd : %s :: args : %s :: kwargs : %s" %
                     (request.proc_name, request.args, request.kwargs))
        if request.proc_name in self.remote_cmds:
            func = self.remote_cmds[request.proc_name]
            try:
                result = func(*request.args, **request.kwargs)
                rpc_response = RPCResponse(request.id, result)
            except Exception as e:
                exception = RemoteXMPPException(e.message)
                rpc_response = RPCResponse(request.id, exception)
            self.client.send_message(rpc_response.dumps(), self.remote_jid)

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

    @remote
    def hello(self, *args, **kwargs):
        return NotImplemented

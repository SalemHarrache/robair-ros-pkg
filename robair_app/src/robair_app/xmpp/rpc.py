import uuid
import cPickle as pickle
from robair_common.logger import LOGGER
from robair_common.utils import retry
from Queue import Empty


def remote(*args, **kwargs):
    """Decorator for remote xmpp methods"""

    def decorate(func, threaded=False):
        setattr(func, '_xmpp_remote', True)
        setattr(func, '_xmpp_remote_threaded', threaded)
        return func

    if len(args):
        return decorate(args[0], **kwargs)
    else:
        return lambda func: decorate(func, **kwargs)


class RemoteXMPPException(Exception):
    '''Exception that happens when the remote method call failled'''
    pass


class RemoteXMPPTimeout(Exception):
    '''Exception that happens when the remote method call failled'''
    def __str__(self):
        return self.__doc__


class RemoteXMPPProxy(object):
    """ RemoteXMPPProxy """
    def __init__(self, client, remote_jid):
        self.client = client
        self.remote_jid = remote_jid
        self.queue = self.client.response_queue

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

    def __rpc_wait_response(self, excepted_request_id, timeout=10):
        remaining_timeout = timeout
        timeout_step = 0.1
        while True:
            try:
                rpc_message = self.queue.get(timeout=timeout_step)
                # TODO: avoid memory leak by removing orphan RPC responses
                if rpc_message.request_id == excepted_request_id:
                    return rpc_message.data
                else:
                    self.response_queue.put(rpc_message)
            except Empty:
                pass
            except KeyboardInterrupt:
                break
            remaining_timeout = remaining_timeout - timeout_step
            if remaining_timeout <= 0:
                raise RemoteXMPPTimeout()

    def __rpc_send(self, name, *args, **kwargs):

        LOGGER.debug('run remote_method %s(%s, %s)' % (name, args, kwargs))
        rpc_request = RPCRequest(name, *args, **kwargs)
        self.client.send_message(self.remote_jid, rpc_request.dumps())
        return self.__rpc_wait_response(rpc_request.id)

    def __getattr__(self, name):
        return lambda *args, **kwargs: self.__rpc_send(name, *args, **kwargs)


class RPCMessage(object):
    def dumps(self):
        return pickle.dumps(self)

    @classmethod
    def loads(cls, data):
        return pickle.loads(data)

    def __repr__(self):
        return "%s" % self


class RPCRequest(RPCMessage):
    def __init__(self, proc_name, *args, **kwargs):
        self.id = str(uuid.uuid4())
        self.proc_name = proc_name
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return "RPCRequest(%s, *%s, **%s)" % (repr(self.proc_name),
                                              repr(self.args),
                                              repr(self.kwargs))


class RPCResponse(RPCMessage):
    def __init__(self, request_id, data):
        self.id = str(uuid.uuid4())
        self.request_id = request_id
        self.data = data

    def __str__(self):
        return "RPCResponse(%s, %s)" % (repr(self.request_id),
                                        repr(self.data))

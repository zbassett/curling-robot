from socket_server.namespace import EventNamespace


class Namespace(EventNamespace):

    def client_connected(self, client):
        super(Namespace, self).client_connected(client)

        print 'Send ping'
        self.emit_to(client, 'ping')

    def register_callbacks(self):
        return {
            'pong': self.pong
        }

    def pong(self, client, **kwargs):
        print 'Received pong event'
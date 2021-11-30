import socket
        
def build_template(input_class):
    class Template(input_class):
        def __init__(self, IP, SEND_PORT, RECV_PORT) -> None:
            super(Template, self).__init__()
            self.UDP_IP = IP
            self.UDP_SEND_PORT = SEND_PORT
            self.UDP_RECV_PORT = RECV_PORT
            self.sock = socket.socket(socket.AF_INET, # Internet
                                    socket.SOCK_DGRAM) # UDP
            self.sock.bind((IP, RECV_PORT))
            
        def __repr__(self) -> str:
            IP = "UDP target IP: %s" % self.UDP_IP
            SEND_PORT = "UDP target port: %s" % self.UDP_SEND_PORT
            RECV_PORT = "UDP target port: %s" % self.UDP_RECV_PORT
            return "\n".join([IP, SEND_PORT, RECV_PORT])

        '''
        Sending by UDP
            Unreliable Data Transmisson
        '''
        def udt_send(self, message):
            assert(isinstance(message, bytes))
            self.sock.sendto(message, (self.UDP_IP, self.UDP_SEND_PORT))
            
        def udt_recv(self):
            return self.sock.recv(self.PKT_SZ)
        
        def close(self):
            self.sock.close()
    return Template
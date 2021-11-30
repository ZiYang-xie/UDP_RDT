from template import build_template
from utils import check_args, PORTOCOL
import sys

def build_sender(portocol):
    class Sender(build_template(portocol)):
        def __init__(self, IP, SEND_PORT, RECV_PORT) -> None:
            super().__init__(IP, SEND_PORT, RECV_PORT)
            
        def Send(self, data):
            self.send(data)
    return Sender
   
if __name__ == "__main__":
    if(check_args(sys.argv) is False):
        sys.exit(1)
        
    ip = '127.0.0.1'
    send_port = 5005
    recv_port = 5006
    
    Sender = build_sender(PORTOCOL[sys.argv[1]])
    sender = Sender(ip, send_port, recv_port)
    
    with open('./data/send_file/large', 'rb') as f:
        data = f.read()
        
    sender.Send(data)
    print("[Send Done]")
    sender.stop_timer()
    sender.close()
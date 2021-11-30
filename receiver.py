from template import build_template
from utils import check_args, PORTOCOL
import sys

def build_receiver(portocol):
    class Receiver(build_template(portocol)):
        def __init__(self, IP, SEND_PORT, RECV_PORT) -> None:
            super().__init__(IP, SEND_PORT, RECV_PORT)
            self.buffer = []
            
        def Recv(self):
            while(True):
                data = self.recv()
                self.buffer.extend(data)
                if(data[-1]['PKG_LEN'] == 0):
                    self.to_app_layer()
                    break
            
        def to_app_layer(self):
            print("[Data Received]")
            result = ''
            for pkt in self.buffer:
                result += pkt['DATA'].decode('utf-8')
            result = result.strip('\0')
            print(f"Len: {len(result)}")
            self.save_file('./data/recv_file/received', result)

        def save_file(self, filePath, data):
            with open(filePath, 'w+') as f:
                f.write(data)
            
    return Receiver
        
if __name__ == "__main__":
    if(check_args(sys.argv) is False):
        sys.exit(1)
        
    ip = '127.0.0.1'
    send_port = 5006
    recv_port = 5005
        
    Receiver = build_receiver(PORTOCOL[sys.argv[1]])
    receiver = Receiver(ip, send_port, recv_port)
    print("Initialized, Wait For Data~")
    receiver.Recv()
    receiver.close()
        
        
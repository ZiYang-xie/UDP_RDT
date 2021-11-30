import struct
import threading

class RDT():
    def __init__(self, MSS=1024, TimeOut=0.1) -> None:
        self.MSS = MSS
        self.HEAD_SZ = 4 * len(struct.pack('!i', 0))
        self.PKT_SZ = self.MSS + self.HEAD_SZ
        self.TimeOut = TimeOut
        
    def start_timer(self):
        self.timer = threading.Timer(self.TimeOut, self.timeout)
        self.timer.setDaemon(True)
        self.timer.start()
        
    def stop_timer(self):
        self.timer.cancel()
    
    def timeout(self):
        print('[Timeout]')
        self.stop_timer()
        self.resend()
        self.start_timer()
    
    def calc_checksum(self, pkt):
        assert(isinstance(pkt['DATA'], bytes))
        check_sum = pkt['SEQ_N'] + pkt['ACK_N']
        check_sum += sum(pkt['DATA'])
        return check_sum
    
    def init_pkt(self):
        pkt = {}
        pkt['SEQ_N'] = 0
        pkt['ACK_N'] = 0
        pkt['PKG_LEN'] = 0
        pkt['DATA'] = bytearray(self.MSS)
        pkt['CHECK_SUM'] = 0
        return pkt
    
    def make_pkt(self, seq_num, ack_num, pkg_len, payload: bytes) -> dict:
        pkt = self.init_pkt()
        pkt['SEQ_N'] = seq_num
        pkt['ACK_N'] = ack_num
        pkt['PKG_LEN'] = pkg_len
        pkt['DATA'][0:len(payload)] = payload
        pkt['DATA'] = bytes(pkt['DATA'])
        pkt['CHECK_SUM'] = self.calc_checksum(pkt)
        return pkt
        
    def get_pkt_num(self, content: bytes):
        length = len(content) 
        
        last = 0 if length % self.MSS == 0 else 1
        pkt_num = length // self.MSS + last
        return pkt_num
    
    def check_pkt(self, pkt: dict) -> bool:
        return pkt['CHECK_SUM'] == self.calc_checksum(pkt)
    
    def is_ack(self, pkt: dict, ack_num: int) -> bool:
        return pkt['SEQ_N'] < 0 and pkt['ACK_N'] == ack_num
    
    def is_seq(self, pkt: dict, seq_num: int) -> bool:
        return pkt['ACK_N'] < 0 and pkt['SEQ_N'] == seq_num
    
    def encoder_pkt(self, pkt: dict) -> bytes:
        head = struct.pack('!4i', pkt['SEQ_N'], pkt['ACK_N'], pkt['PKG_LEN'], pkt['CHECK_SUM'])
        raw_bytes = head + pkt['DATA']
        return raw_bytes
    
    def decode_pkt(self, raw_bytes: bytes) -> dict:
        pkt = self.init_pkt()
        pkt['DATA'] = raw_bytes[-self.MSS:]
        head = raw_bytes[:-self.MSS]
        pkt['SEQ_N'], pkt['ACK_N'], pkt['PKG_LEN'], pkt['CHECK_SUM'] = struct.unpack('!4i', head)
        return pkt
    
    def send_pkt(self, pkt: dict):
        print("Send Pkt: Seq[{:d}] | ACK[{:d}]".format(pkt['SEQ_N'], pkt['ACK_N']))
        raw_bytes = self.encoder_pkt(pkt)
        self.udt_send(raw_bytes)
        
    def recv_pkt(self) -> dict:
        raw_data = self.udt_recv()
        pkt = self.decode_pkt(raw_data)
        return pkt
    
    def send_ack(self, ack_num: int):
        pkt = self.make_pkt(-1, ack_num, -1, b'ACK')
        self.send_pkt(pkt)
    
    def send(self, content: bytes):   
        raise NotImplementedError
    
    def recv(self):   
        raise NotImplementedError
    
    def resend(self):
        raise NotImplementedError
    
    def udt_send(self, message):
        raise NotImplementedError
    
    def udt_recv(self):
        raise NotImplementedError
    
    
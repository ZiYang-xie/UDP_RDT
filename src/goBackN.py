from .rdt import RDT

class goBackN(RDT):
    def __init__(self, window_len=10) -> None:
        super(goBackN, self).__init__()
        self.sender_buffer = []
        self.window_len = window_len
        self.left_side = 0
        self.right_side = 0
        self.seq_n = -1
        self.ack_n = 0
        self.UPPER_N = self.window_len + 1
        # window = [left_side, right_size）
        
    def is_ack(self, pkt: dict):
        return pkt['SEQ_N'] < 0 and pkt['ACK_N'] != self.seq_n
    
    def change_state(self, step: int):
        self.left_side += step
        self.right_side = min(self.right_side + step, self.pkt_num)
        self.seq_n = (self.seq_n + step) % self.UPPER_N
        
    def save_to_buffer(self, pkt_num: int, content: bytes) -> None:
        offset = 0
        seq_n = 0
        for i in range(pkt_num):
            pkt_send = self.make_pkt(seq_n, -1, pkt_num - i - 1, content[offset:offset+self.MSS])
            self.sender_buffer.append(pkt_send)
            seq_n = (seq_n + 1) % self.UPPER_N
            offset += self.MSS
            
    def send_range(self, left, right):
        idx = left
        while(idx != right):
            pkt_send = self.sender_buffer[idx]
            self.add_send_time(1)
            self.send_pkt(pkt_send)
            idx += 1
            
    def resend(self):
        self.send_range(self.left_side, self.right_side)
        
    def send(self, content: bytes) -> None:   
        self.pkt_num = self.get_pkt_num(content)
        self.right_side = min(self.left_side + self.window_len, self.pkt_num)
        self.inform(f"Total Pkt Num = {self.pkt_num}")
        self.save_to_buffer(self.pkt_num, content)
        
        self.send_range(self.left_side, self.right_side)
        self.start_timer()
        
        while(self.left_side != self.right_side):
            pkt_recv = self.recv_pkt()
        
            if(self.check_pkt(pkt_recv) and self.is_ack(pkt_recv)):
                self.inform(f"Recv Right ACK{pkt_recv['ACK_N']}")
                self.stop_timer()    
                step = (pkt_recv['ACK_N'] - self.seq_n) % self.UPPER_N
                if(step):
                    self.add_success_time(step)
                    send_step = min(step, self.pkt_num - self.right_side)
                    self.send_range(self.right_side, self.right_side + send_step)
                    self.start_timer()
                    self.change_state(step)
            else:
                self.inform(f"Recv Wrong ACK{pkt_recv['ACK_N']}, Dropping")
                
        if(self.Test_mode):
            self.print_test_result()
        
    def recv(self) -> list:
        result = None
        while(result is None):
            pkt_recv = self.recv_pkt()
            if(self.check_pkt(pkt_recv) and self.is_seq(pkt_recv, self.ack_n)):
                self.inform(f"Recv Right Seq{pkt_recv['SEQ_N']}")
                self.send_ack(pkt_recv['SEQ_N'])
                self.ack_n = (self.ack_n + 1) % self.UPPER_N 
                result = [pkt_recv]
            else:
                last_ack = (self.ack_n - 1) % self.UPPER_N 
                self.inform(f"Recv Wrong Seq{pkt_recv['SEQ_N']}, resend ACK{last_ack}")
                self.send_ack(last_ack)
                
        return result
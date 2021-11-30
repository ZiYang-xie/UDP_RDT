from .rdt import RDT

class selRepeat(RDT):
    def __init__(self, window_len=10) -> None:
        super(selRepeat, self).__init__()
        self.window_len = window_len
        self.sender_buffer = []
        self.receiver_buffer = [0] * self.window_len
        self.sender_mark = [0] * self.window_len
        self.receiver_mark = [0] * self.window_len
        self.pkg_unreceived = None
        self.left_side = 0
        self.right_side = 0
        self.seq_n = -1
        self.ack_n = 0
        self.UPPER_N = 2*self.window_len
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
            pkt_send = self.make_pkt(seq_n, -1, self.pkt_num - i - 1,content[offset:offset+self.MSS])
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
        resend_pkt = self.sender_buffer[self.left_side]
        self.send_pkt(resend_pkt)
        self.add_send_time(1)
        
    def mark_pkt(self, buffer, offset):
        buffer[offset] = 1
        
    def get_window_shift(self, buffer):
        idx = 0
        while(idx != self.window_len and buffer[idx]):
            idx += 1
        return idx
        
    def send(self, content: bytes) -> None:   
        assert(len(self.sender_buffer) == 0)
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
                offset = (pkt_recv['ACK_N'] - self.seq_n - 1) % self.window_len
                self.mark_pkt(self.sender_mark, offset)
                step = self.get_window_shift(self.sender_mark)
                
                if(step):
                    self.add_success_time(step)
                    self.stop_timer()
                    send_step = min(step, self.pkt_num - self.right_side)
                    self.send_range(self.right_side, self.right_side + send_step)
                    self.sender_mark = self.sender_mark[step:] + [0]*step
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
            if(self.check_pkt(pkt_recv) and (self.pkg_unreceived == None or pkt_recv['PKG_LEN'] <= self.pkg_unreceived)):
                self.inform(f"Recv Right Seq{pkt_recv['SEQ_N']}")
                self.send_ack(pkt_recv['SEQ_N'])
                
                if(self.pkg_unreceived is None):
                    self.pkg_unreceived = pkt_recv['PKG_LEN']
                    
                offset = self.pkg_unreceived - pkt_recv['PKG_LEN']
                self.mark_pkt(self.receiver_mark, offset)
                self.receiver_buffer[offset] = pkt_recv
                
                step = self.get_window_shift(self.receiver_mark)
                if(step):
                    self.pkg_unreceived -= step
                    right_step = min(step, self.pkg_unreceived)
                    self.ack_n = (self.ack_n + right_step) % self.UPPER_N 
                    result = self.receiver_buffer[:step]
                    self.receiver_mark = self.receiver_mark[step:] + [0]*step
                    self.receiver_buffer = self.receiver_buffer[step:] + [0]*step
                
            else: 
                self.inform(f"Recv Wrong Seq{pkt_recv['SEQ_N']}, resend ACK{pkt_recv['SEQ_N']}")
                self.send_ack(pkt_recv['SEQ_N'])
                
        return result
from .rdt import RDT

class altBit(RDT):
    def __init__(self) -> None:
        super(altBit, self).__init__()
        self.state = 0
        
    def change_state(self):
        # AltBit toggle state
        self.state = int(1 - self.state)
        
    def resend(self):
        self.send_pkt(self.pkt_send)
        self.add_send_time(1)
    
    def send(self, content: bytes) -> None:   
        pkt_num = self.get_pkt_num(content)
        self.inform(f"Total Pkt Num = {pkt_num}")
        offset = 0
        
        for i in range(pkt_num):
            self.inform(f"Sending Pkt Num = {i+1}")
            self.add_send_time(1)  
            self.pkt_send = self.make_pkt(self.state, -1, pkt_num - i - 1, content[offset:offset+self.MSS])
            self.send_pkt(self.pkt_send)
            self.start_timer()
            pkt_recv = self.recv_pkt()
            self.stop_timer()
            
            if(self.check_pkt(pkt_recv) and self.is_ack(pkt_recv, self.state)):
                self.inform(f"Recv Right ACK{self.state}")
                self.add_success_time(1)
                self.change_state()    
            else:
                self.inform(f"Recv Wrong ACK, resend Seq{self.state}")
                self.resend()
                self.start_timer()
                
            offset += self.MSS
        
        if(self.Test_mode):
            self.print_test_result()
            
    def recv(self) -> list:
        result = None
        while(result is None):
            pkt = self.recv_pkt()
            if(self.check_pkt(pkt) and self.is_seq(pkt, self.state)):
                self.send_ack(pkt['SEQ_N'])
                self.change_state()
                result = [pkt]
            else:
                self.send_ack(not self.state)
                
        return result
        
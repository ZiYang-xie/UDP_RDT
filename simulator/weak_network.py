import sys
import os

def flush_dnctl():
    os.system("sudo dnctl -q flush")

def set_rules(filePath):
    os.system(f"sudo pfctl -f {filePath}")

def clear_rules():
    os.system("sudo pfctl -f /etc/pf.conf")

def set_network(bw, delay, loss):
    os.system(f"sudo dnctl pipe 1 config bw {bw} delay {delay} plr {loss}")

if __name__ == "__main__":
    bw = 0
    delay = 0
    loss = 0.05
    if(sys.argv[1] == 'set'):
        set_network(bw, delay, loss)
        set_rules("./simulator/udp_rule")
    elif(sys.argv[1] == 'reset'):
        clear_rules()
        flush_dnctl()
    
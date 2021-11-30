import sys

def usage(argv):
    print(f"Usage: python {argv[0]} <file_name> <line_num>")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage(sys.argv)
        sys.exit(1)
        
    file_name = sys.argv[1]
    size = int(sys.argv[2])
    
    with open(f'./data/send_file/{file_name}', 'w+') as f:
        for i in range(size):
            f.writelines(f'line{i}\n')
        
    
    
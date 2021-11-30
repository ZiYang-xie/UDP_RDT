from src import altBit, goBackN, selRepeat

PORTOCOL = {
    'ab': altBit,
    'gbn': goBackN,
    'sr': selRepeat
}

def check_args(argv):
    if(len(argv) != 2):
        print(f"Usage: python {argv[0]} <portocol>")
        return False
    if(argv[1] not in PORTOCOL.keys()):
        print("「Support Portocols」:")
        for portocol in list(PORTOCOL.keys()):
            print(f'- {portocol}')
        return False
    return True
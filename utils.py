

def get_bitlist(num, size=8):
    #[int(n) for n in bin(0x15)[2:].zfill(8)]
    return [int(digit) for digit in bin(num)[2:].zfill(size)]


def get_int(bitlist):
    out = 0
    for bit in bitlist:
        out = (out << 1) | bit
    return out
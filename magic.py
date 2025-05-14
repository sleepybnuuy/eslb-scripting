PART_DEFINITION = b'\x00\x00\x00\x01'
PART_FOOTER_A = b'p\x00\x00\x00'
PART_FOOTER_B = b'p\x00\n\x00'
PART_FOOTER_MAGIC = b'\x04\x00\x00\x00\x01\x00\x00\x00'

PARTIAL_DEFINITION = b'\x00\x00\x03\x00'
PARTIAL_MAGIC = b'\x04\x00\x00\x00'

HEADER_MAGIC = bytes([
    0x14, 0x00, 0x00, 0x00, 0x45, 0x53, 0x4C, 0x42, 0x00, 0x00, 0x0A, 0x00, 0x08, 0x00, 0x00, 0x00, 
    0x00, 0x00, 0x04, 0x00, 0x0A, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 
])

def zero_padding(num):
    return bytes([0 for x in range(num)])

def ff_padding(num):
    return bytes([255 for x in range(num)])

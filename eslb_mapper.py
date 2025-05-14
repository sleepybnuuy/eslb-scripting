'''
enum PartType : u32 {
    a = 0x70000000,
    b = 0x70000A00
};

struct Part {
    u16 checksum;
    padding[2]; // prepended FF FF
    padding[4]; // part definition 00 00 00 01 THIS CAN BE MISSING
    u32 part_id; // p####
    padding[8]; // footer 04 00 00 00 01 00 00 00
    be PartType part_type; // 70 00 00 00 if standard; 70 00 0A 00 if unk
};

struct WeaponPartial {
    u16 checksum;
    padding[2]; // prepended FF FF
    padding[4]; // prepended 00 00 03 00
    u32 weapon_id; // w####
    padding[4]; // 04 00 00 00 unk magic
    u32 num_parts;
    /*
    each longword is the distance from start of longword to the corresponding part,
    these are in reverse order
    ex: (last will be 04 00 00 00 as its 8 bytes away from start of Part)
    */
    u32 part_references[num_parts];
    Part parts[num_parts];
};

struct ESLBHeader {
    padding[4]; // 14 00 00 00 ; # bytes after ESLB string til num partials
    padding[4]; // 45 53 4C 42 ; ESLB
    padding[20]; // unknown magic
    u32 num_partials; // total WeaponPartial definitions in file
    /*
    each longword is the distance from start of longword to the corresponding partial,
    these are in reverse order
    ex: (last will be 04 00 00 00 as its 8 bytes away from start of Partial)
    */
    u32 partial_references[num_partials];
};

ESLBHeader header @ 0x00000000;
// WeaponPartial partials[header.num_partials] @ 0x00000130;

// 38 00 00 00 20 00 00 00 04 00 00 00 8A F4 FF FF 00 00 00 01 32 00 00 00 04 00 00 00 01 00 00 00 70 00 00 00 A0 F7 FF FF 27 00 00 00 04 00 00 00 01 00 00 00 70 00 00 00
// Parts can be shortened at times missing the 0 0 0 1 definition head
'''

import mmap
from structs import *

def deserialize_eslb(path: str):
    with open(path,'r') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
            header = m.read(28)
            num_partials = int.from_bytes(m.read(4), byteorder='little')

            print(f'header: {header}')
            print(f'partial count: {num_partials}')

            for ref in range(num_partials):
                offset = int.from_bytes(m.read(4), byteorder='little')
                # savepoint cursor position in header blob
                current_pos = m.tell()

                # try to parse a partial thats [offset] bytes away
                try:
                    partial = partial_from_offset(offset, m)
                except:
                    print('exc')
                finally:
                    # return to header to parse next ref
                    m.seek(current_pos)


def partial_from_offset(offset, m):
    m.seek(m.tell() + offset - 4)
    checksum = m.read(2)
    m.read(2)
    m.read(4) # 00 03 00 00
    weapon_id = int.from_bytes(m.read(4), byteorder='little')
    m.read(4) # 04 00 00 00
    num_parts = int.from_bytes(m.read(4), byteorder='little')
    print(f'w{weapon_id:0>4} - {num_parts} parts')

    for ref in range(num_parts):
        part_offset = int.from_bytes(m.read(4), byteorder='little')
        current_pos = m.tell()

        try:
            part = part_from_offset(part_offset, m)
        except:
            print('exc')
        finally:
            m.seek(current_pos)

def part_from_offset(offset, m):
    m.seek(m.tell() + offset - 4)
    checksum = m.read(2)
    m.read(2)
    definition = m.read(4)
    part_id = int.from_bytes(m.read(4), byteorder='little')
    m.read(8) # 04 00 00 00 01 00 00 00
    footer = m.read(4)
    print(f'part p{part_id:0>4}')

def main():
    deserialize_eslb('data/extra_weapon.eslb')

main()

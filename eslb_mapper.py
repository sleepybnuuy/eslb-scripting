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
import os
from structs import *

def deserialize_eslb(path: str):
    with open(path,'r') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
            header = m.read(28)
            partial_count = int.from_bytes(m.read(4), byteorder='little')

            print(f'header: {header}')
            print(f'partial count: {partial_count}')

            complete_refs = []
            for ref in range(partial_count):
                offset = int.from_bytes(m.read(4), byteorder='little')
                # savepoint cursor position in header blob
                current_pos = m.tell()

                # try to parse a partial thats [offset] bytes away
                try:
                    partial = partial_from_offset(offset, m)
                    if not partial:
                        raise
                    complete_refs.append(PartialRef(offset, partial))
                except:
                    print('except')
                    continue
                finally:
                    # return to header to parse next ref
                    m.seek(current_pos)

            if len(complete_refs) != partial_count:
                print(f'error: parsed {len(complete_refs)} partials, expected {partial_count}')
            data = EslbData(partial_count, complete_refs)
            m.close()
        f.close()
    return data


def partial_from_offset(offset, m):
    m.seek(m.tell() + offset - 4)
    checksum = m.read(2)
    m.read(2) # FF FF

    m.read(4) # 00 03 00 00
    weapon_id = int.from_bytes(m.read(4), byteorder='little')
    m.read(4) # 04 00 00 00
    part_count = int.from_bytes(m.read(4), byteorder='little')
    # print(f'w{weapon_id:0>4} - {part_count} parts')

    complete_refs = []
    for ref in range(part_count):
        part = None
        part_offset = int.from_bytes(m.read(4), byteorder='little')
        current_pos = m.tell()

        try:
            part = part_from_offset(part_offset, m)
            if not part:
                raise
        except:
            print('exc')
            continue
        finally:
            m.seek(current_pos)

        complete_refs.append(PartRef(offset, part))

    if len(complete_refs) != part_count:
        print(f'error: parsed {len(complete_refs)} parts, expected {part_count}')
    return Partial(checksum, weapon_id, part_count, complete_refs)

def part_from_offset(offset, m):
    m.seek(m.tell() + offset - 4)
    checksum = m.read(2)
    m.read(2) # FF FF

    definition = m.read(4)
    if not part_has_valid_definition(definition):
        print(f'unknown definition on part: {definition}')
        return

    part_id = int.from_bytes(m.read(4), byteorder='little')
    m.read(8) # 04 00 00 00 01 00 00 00

    footer = m.read(4)
    part_type = PART_FOOTER_MAP.get(footer)
    if not part_type:
        print(f'key error for unknown footer: {footer}')
        return

    return Part(checksum, part_id, part_type)

def serialize_eslb(data: EslbData, path: str):
    output = data.to_bytes()
    with open(path,'wb') as f:
        f.truncate(len(output))
        f.write(output)
        f.flush()
        f.close()
    return

def main():
    data = deserialize_eslb('data/extra_weapon.eslb')
    print(data)
    print(data.to_bytes())
    serialize_eslb(data, 'data/COMPILED_extra_weapon.eslb')
    print('done')

main()

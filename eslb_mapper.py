import mmap
from structs import *
from serialize import *

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

        complete_refs.append(PartRef(part_offset, part))

    if len(complete_refs) != part_count:
        print(f'error: parsed {len(complete_refs)} parts, expected {part_count}')
    return Partial(checksum, weapon_id, len(complete_refs), complete_refs)

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

def printout_eslb(data: EslbData, path: str):
    output = data.to_bytes()
    with open(path,'wb') as f:
        f.truncate(len(output))
        f.write(output)
        f.flush()
        f.close()
    return

def append_eslb(inputs, in_path: str, out_path: str):
    with open(in_path,'r') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
            base_header = m.read(28)
            base_weapon_count = int.from_bytes(m.read(4), byteorder='little')
            base_offsets = m.read(4 * base_weapon_count)
            base = m.read()

    initial_weapon_offset = int.from_bytes(base_offsets[:4], byteorder='little')
    append_offsets, append_weapons = serialize_appends(inputs, initial_weapon_offset)

    combined_weapon_count = base_weapon_count + len(inputs)
    combined_weapon_bytes = combined_weapon_count.to_bytes(4, 'little')
    with open(out_path,'wb') as f:
        f.truncate(sum([len(i) for i in [base_header, combined_weapon_bytes, append_offsets, base_offsets, base, append_weapons]]))
        f.write(base_header) # header copied from base
        f.write(combined_weapon_bytes) # combined weapon count
        f.write(append_offsets) # append offsets
        f.write(base_offsets) # base offsets
        f.write(base) # base file contents
        f.write(append_weapons) # append contents
        f.flush()
        f.close()

    return

def main():
    # data = deserialize_eslb('data/extra_weapon.eslb')
    # inputs = data.to_inputs()
    # compiled_eslb = serialize_eslb(inputs)
    # printout_eslb(compiled_eslb, 'data/COMPILED_extra_weapon.eslb')

    # fetch existing weapons and parts, append will calculate new headers so we dgaf about those
    # data = deserialize_eslb('data/extra_weapon.eslb')
    # inputs = data.to_inputs()

    # test inputting w1735b0001 AND w2001b0061to diff with w1735-plus-w2001-b61.eslb
    inputs = [(1735, [1,2]), (2001, [61])]
    append_eslb(inputs, 'data/extra_weapon.eslb', 'data/APPENDED_extra_weapon.eslb')

    print('done')

main()

# chara/xls/extraskl/extra_weapon.eslb

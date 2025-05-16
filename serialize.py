from structs import *
from magic import *
import struct

def part_ref_offset(index, count) -> int:
    '''for a part ref at [index] of [count] refs, return its offset value'''
    return 4 * (count-index) + 24 * (count-index-1)

def weapon_size(parts_count) -> int:
    '''weapon size = 20 header (check, FF, start, ID, magic, count) + 4 * parts count (offsets) + 24 * parts count'''
    return 20 + 28 * parts_count

def weapon_ref_offset(index, count, next_weapons) -> int:
    '''4 bytes per offset plus total size of upcoming weapons'''
    return 4 * (count-index) + sum([weapon_size(len(wep[1])) for wep in next_weapons])

def weapon_key(index, inputs) -> int:
    '''
w418
EE FE = 65262 => 274
396 bytes left in file
122 diff

    for the actual weapon's checksum, take distance to end of file (sum of sizes of self and all upcoming weapons)
    subtract that from 65536
    add 122
    index = position in weapon list
    weapons = full weapon list
    '''
    seq_pos = len(inputs) - index
    return 65536 - sum([weapon_size(len(wep[1])) for wep in inputs[:index+1]]) + 122

def part_key(part_index, weapon_index, inputs) -> int:
    '''
2 parts
B2 FE = 65202 = 334
368 bytes left in file = 34

CA FE = 65226 = 310
344 bytes left in file = 34

    for a part's checksum, take distance to end of file (size of remaining parts and all upcoming weapons)
    subtract that from 65536
    add 34
    part_index = # part we're on
    weapon_index = # weapon we're on
    weapons = full weapon list
    '''
    seq_pos = len(inputs) - weapon_index
    part_seq_pos = len(inputs[weapon_index][1]) - part_index
    return 65536 - (sum([24 for p in (inputs[weapon_index][1][part_seq_pos-1:])]) + sum([weapon_size(len(wep[1])) for wep in inputs[seq_pos+1:]])) + 34

def pack_checksum(value: int) -> bytearray:
    if value > 65536:
        packed = bytearray(struct.pack("<H", value-65536))
        packed.extend(zero_padding(2))
    else:
        packed = bytearray(struct.pack("<H", value))
        packed.extend(ff_padding(2))
    return packed


def serialize_eslb(inputs: List[tuple[int, List[int]]]):
    '''
    given inputs, spit out a compiled EslbData
    input tuple: (weapon ID, [part IDs...])

    [(2001, [1, 2, 17]), (2002, [1]), ...]
    '''

    # sort inputs and parts by ascending IDs
    inputs.sort(key=lambda x: x[0])
    for w,p in inputs:
        p = sorted(p)

    weapon_refs = []
    for i, (weapon, parts) in enumerate(inputs):
        part_refs = []
        for i2, part_id in enumerate(parts):
            # last checksum will be 0A 00 00 00 or 65546
            check_value = part_key(i2, i, inputs)
            part_refs.append(PartRef(
                offset=part_ref_offset(i2, len(parts)),
                part=Part(
                    checksum=pack_checksum(check_value),
                    part_id=part_id,
                    part_type=PartType.A, # force to type A
                )
            ))

        check_value = weapon_key(i, inputs)
        weapon_refs.append(PartialRef(
            offset=weapon_ref_offset(i, len(inputs), inputs[i+1:]),
            partial=Partial(
                checksum=pack_checksum(check_value),
                weapon_id=weapon,
                part_count=len(part_refs),
                part_refs=part_refs,
            )
        ))

    return EslbData(
        partial_count=len(inputs),
        partial_refs=weapon_refs
    )

from structs import *
from magic import *
import random
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

def make_key(keys: set) -> tuple[int, set]:
    '''generate a dummy offset int and add to set, returning edited set and new key'''
    added = False
    key = 0
    while not added:
        key = random.randint(0, 255**2)
        size = len(keys)
        keys.add(key)
        added = size != len(keys)

    return key, keys

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

    checksums = set()
    weapon_refs = []
    for i, (weapon, parts) in enumerate(inputs):
        part_refs = []
        for i2, part_id in enumerate(parts):
            key, checksums = make_key(checksums)
            part_refs.append(PartRef(
                offset=part_ref_offset(i2, len(parts)),
                part=Part(
                    checksum=struct.pack("<H", key),
                    part_id=part_id,
                    part_type=PartType.A, # force to type A
                )
            ))

        key, checksums = make_key(checksums)
        weapon_refs.append(PartialRef(
            offset=weapon_ref_offset(i, len(inputs), inputs[i+1:]),
            partial=Partial(
                checksum=struct.pack("<H", key),
                weapon_id=weapon,
                part_count=len(part_refs),
                part_refs=part_refs,
            )
        ))

    return EslbData(
        partial_count=len(inputs),
        partial_refs=weapon_refs
    )

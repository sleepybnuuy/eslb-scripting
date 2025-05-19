from dataclasses import dataclass
from typing import List
from enum import Enum
from magic import *

class PartType(Enum):
    A = 0 # footer 0x70000000
    B = 1 # footer 0x70000A00 -> 10 00 08 00 -> xx xx xx xx -> 0A 00 00 00
    '''
    type B implies 3 extra longwords before next part or partial (last of these 0A000000)
    in case of w113 (3 parts), 2nd part is type B, then 3rd part is missing its checksum?
    '''

PART_FOOTER_MAP = {
    PART_FOOTER_A: PartType.A,
    PART_FOOTER_B: PartType.B
}

@dataclass
class Part:
    checksum: bytearray
    part_id: int
    part_type: PartType

    def to_bytes(self) -> bytearray:
        out = bytearray()
        out.extend(self.checksum) # AB CD FF FF (or 00 00)
        out.extend(PART_DEFINITION) # 00 00 00 01
        out.extend(self.part_id.to_bytes(4, 'little')) # ID 00 00 00
        out.extend(PART_FOOTER_MAGIC) # 04 00 00 00 01 00 00 00
        out.extend(PART_FOOTER_A) # force support for footer A since type B is unknown

        return out

@dataclass
class PartRef:
    offset: int
    part: Part

    def to_bytes(self) -> bytearray:
        out = bytearray()
        out.extend(self.offset.to_bytes(4, 'little'))

        return out

@dataclass
class Partial:
    checksum: bytearray
    weapon_id: int
    part_count: int
    part_refs: List[PartRef]

    def to_bytes(self) -> bytearray:
        out = bytearray()
        out.extend(self.checksum) # AB CD FF FF (or 00 00)
        out.extend(PARTIAL_DEFINITION)
        out.extend(self.weapon_id.to_bytes(4, 'little'))
        out.extend(PARTIAL_MAGIC)
        out.extend(len(self.part_refs).to_bytes(4, 'little')) # using actual length, not part_count!
        for ref in self.part_refs:
            out.extend(ref.to_bytes())
        for ref in self.part_refs:
            out.extend(ref.part.to_bytes())

        return out

@dataclass
class PartialRef:
    offset: int
    partial: Partial

    def to_bytes(self) -> bytearray:
        out = bytearray()
        out.extend(self.offset.to_bytes(4, 'little'))

        return out

@dataclass
class EslbData:
    partial_count: int
    partial_refs: List[PartialRef]

    def to_bytes(self) -> bytearray:
        out = bytearray()
        out.extend(HEADER_MAGIC)
        out.extend(len(self.partial_refs).to_bytes(4, 'little')) # using actual refs length, not partial_count!
        for ref in self.partial_refs:
            out.extend(ref.to_bytes())
        for ref in reversed(self.partial_refs):
            out.extend(ref.partial.to_bytes())

        return out

    def to_inputs(self) -> List[tuple[int, List[int]]]:
        return [(partial_ref.partial.weapon_id, [part_ref.part.part_id for part_ref in partial_ref.partial.part_refs]) for partial_ref in self.partial_refs]

def part_has_valid_definition(definition):
    return definition == PART_DEFINITION

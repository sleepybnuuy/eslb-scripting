from dataclasses import dataclass
from typing import List
from enum import Enum

class PartType(Enum):
    A = 0 # footer 0x70000000
    B = 1 # footer 0x70000A00 -> 10 00 08 00 -> xx xx xx xx -> 0A 00 00 00

'''
type B implies 3 extra longwords before next part or partial (last of these 0A000000)
in case of w113 (3 parts), 2nd part is type B, then 3rd part is missing its checksum?
'''

@dataclass
class Part:
    checksum: bytes
    has_definition: bool
    part_id: int
    part_type: PartType

@dataclass
class PartRef:
    offset: int
    part: Part

@dataclass
class Partial:
    checksum: bytes
    weapon_id: int
    part_count: int
    part_refs: List[PartRef]

@dataclass
class PartialRef:
    offset: int
    partial: Partial

@dataclass
class HeaderInfo:
    partial_count: int
    partial_refs: List[PartialRef]
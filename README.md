# eslb-scripting

## header format
fixed header, followed by:
- count of weapons with partial skeletons in file (`partial_count`)
- list of reference longwords per `partial_count` (`PartialRef`) in FILO order
  - each ref carries an `offset` equalling the # of bytes til the occurence in the file of the partial it references

![eslb_header](https://github.com/user-attachments/assets/ceb81556-4784-43cf-8098-0b844bcbf642)

## data (partial & parts) format
after the header, data is chunked into `Partial` blocks for each weapon in LIFO order:
- partial begins with a unique/arbitrary `checksum` (this is the location that a PartialRef offset points to)
- fixed start of weapon / partial info (`00 00 03 00`) followed by XIV `weapon_id` longword and another magic (`04 00 00 00`)
- count of Parts on this weapon (`part_count`)
- list of reference longwords per `part_count` (`PartRef`) in FILO order
  - as above, offset points to the checksum of the related Part

for each part of a partial,
- checksum is followed by start flag (`00 00 00 01`)
- XIV `part_id` longword
- ending with one of two(?) footer patterns:
  - type A: `04 00 00 00 | 01 00 00 00 | 70 00 00 00`
  - type B: `04 00 00 00 | 01 00 00 00 | 70 00 0A 00`
    - only 2-3 use cases in vanilla eslb file, unknown what its for
    - may indicate an additional set of trailing longwords, terminating with `0A 00 00 00`?

![eslb_data](https://github.com/user-attachments/assets/df50c9ad-1ae4-4437-85ff-02b037c5a0ad)

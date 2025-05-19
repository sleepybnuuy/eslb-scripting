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

for each part of a partial (listed in LIFO order),
- checksum is followed by start flag (`00 00 00 01`)
- XIV `part_id` longword
- ending with one of two(?) footer patterns:
  - type A: `04 00 00 00 | 01 00 00 00 | 70 00 00 00`
  - type B: `04 00 00 00 | 01 00 00 00 | 70 00 0A 00`
    - only 2-3 use cases in vanilla eslb file, unknown what its for
    - may indicate an additional set of trailing longwords, terminating with `0A 00 00 00`?

![eslb_data](https://github.com/user-attachments/assets/df50c9ad-1ae4-4437-85ff-02b037c5a0ad)

## checksums
edits to the base eslb file, e.g. affected weapon IDs or part IDs, without touching any checksums, offsets, or count fields load successfully thru textools. making an ESLB that adds or removes any weapons' skeletons requires, at minimum, edits to the header offsets plus part & partial checksums. xiv does not seem keen to accept arbitrary checksums (changing even one from the base file makes it fail to load), and a couple formulas seem to roughly derive their values:
- part checksum = 65536 - [bytes til EOF] + 34
- weapon checksum = 65536 - [bytes til EOF] + 122

these calculations work for **most** entries in the vanilla file, but inclusions of type B parts and unexpected headers throw off a few results. new checksums derived from this scheme don't currently seem to get us loading either.

## appending to file
adding new weapons _onto_ the vanilla file works like a charm - with the correct formatting and the inclusion of a header offset, the newly added weapon will call for a partial sklb when drawn ingame. 

![image](https://github.com/user-attachments/assets/5233f1f3-e5fb-4b38-862c-160668599049)

the above block has:
- a weapon checksum of 122, derived from the byte distance to the last weapon checksum (checksum2 = checksum1 + distance)
- a weapon ID of 1735
- a part checksum of 58, derived from previous part's checksum
- a part ID of 1

when we equip w1735b0001, reslogger confirms that xiv looked for a skeleton in its parts folder, which in vanilla does not exist. other entries from the file also load w/o issue.

![image](https://github.com/user-attachments/assets/f8dd9ae4-0eb7-414a-b09e-a6ef15653816)

## issues/questions

1. parts added to redefined/vanilla-present weapons call both a phyb and sklb - new weapons added only call an sklb?
2. consequences of redefining type-B weapon parts? can the type-B footers be re-added w/o parsing error?
3. what formatting is needed to author a fully new eslb, not just appending / duping over the existing?
4. does the ESLB resource handler need to be added to clientstructs? what other infra needs to be in place to support eslb metadata?

###  oeminfo-huawei
  
- Used to modify the oeminfo file/storage region on Huawai devices which controls things like the model number and region
- Original code from https://forum.xda-developers.com/p9-plus/how-to/mod-oeminfo-structure-t3446382
- Updated Code: This is a 2024 update of the script, which fixed bugs in the pack function and added usage examples.

```shell
oeminfo_huawei.py [-h] {decode,encode,replace} ...

positional arguments:
  {decode,encode,replace}
    decode   Extracts and decodes the oeminfo image file.
    encode   Encodes the contents of a folder into an oeminfo image file.
    replace  Replaces the contents of an oeminfo image with the contents of a folder.

optional arguments:
  -h, --help            Show this help message and exit
```


#### Detailed Usage example:

 - Requirements: You must have an unlocked bootloader and Magisk installed to modify the oeminfo file/acces to testpoint and flashing with [Huawei Unlock Tool](https://github.com/werasik2aa/Huawei-Unlock-Tool)
 - Tested Environment: Script successfully tested on Ubuntu with Python 3 on a CMR-W09 running EMUI 9.1.0.332. The script was used to change the region from C567 to C432 and hw/usa to hw/eu.

#### Extracting oeminfo Image:
```shell
user@ubuntu:~/oem_info$ adb shell
su
dd if=/dev/block/platform/hi_mci.0/by-name/oeminfo of=/storage/sdcard1/oeminfo.img
adb pull /storage/emulated/0/oeminfo.img eminfo.emmc.win
```
#### Decoding oeminfo Image:
```shell
user@ubuntu:~/oem_info$ python3 oeminfo_huawei.py decode ./oeminfo.img
hdr:OEM_INFO age:  1 id:    1
hdr:OEM_INFO age:  d id:    8
hdr:OEM_INFO age:  1 id:   12 Region
hdr:OEM_INFO age:  1 id:   1c
hdr:OEM_INFO age:  1 id:   33
hdr:OEM_INFO age:  1 id:   34
hdr:OEM_INFO age:  1 id:   35
hdr:OEM_INFO age:  3 id:   43 Root Type (info)
hdr:OEM_INFO age:  1 id:   44 rescue Version
hdr:OEM_INFO age:  1 id:   46
hdr:OEM_INFO age:  1 id:   4d
hdr:OEM_INFO age:  1 id:   4e Rom Version
hdr:OEM_INFO age:  1 id:   51
hdr:OEM_INFO age:  1 id:   61 Hardware Version
hdr:OEM_INFO age:  3 id:   62 PRF?
```
- Output Directory: After decoding, the script creates a directory named based on the hardware version, region, and software version, e.g. "CMR-W09#hw-usa#CMR-W09 8.0.0.200(C567)".
- Editing Files: Modify the files within the output directory using a hex editor like GHex to change the region.

#### Encoding the Modified Files into an Image:
```shell
user@ubuntu:~/oem_info$ python3 oeminfo_huawei.py pack -i CMR-W09#hw-usa#CMR-W09\ 8.0.0.200\(C567\)/ -o ./test.img
None
```

#### Flashing the Modified Image:
```shell
user@ubuntu:~/oem_info$ fastboot flash oeminfo test.img 
target reported max download size of 471859200 bytes
sending 'oeminfo' (65536 KB)...
OKAY [  2.264s]
writing 'oeminfo'...
OKAY [  0.478s]
finished. total time: 2.742s
```

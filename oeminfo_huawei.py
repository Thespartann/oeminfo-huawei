#!/usr/bin/env python3.7
# OEMINFO tool
# rysmario 2016
# Thespartann 2024
#   hackish tool to "unpack" a oeminfo from huawei
#
# I take NO responsibility for a brick, soft brick, alien abduction or anything

# takes arguments "decode", "encode", "replace"
#   decode is optional
#decode oeminfo.bin to folder created from oemeinfo content [i.e. VIE-AL10#all-cn#VIE-C00B176- Rayglobe ]
#   python oeminfo_decode_v2.py [decode] <oeminfo.bin>
#
#replace folder to out_file:
#   python oeminfo_decode_v2.py replae <existing_out_file> <replacement-file>

# Originally from https://forum.xda-developers.com/p9-plus/how-to/mod-oeminfo-structure-t3446382
# Came with no license, but in the OP is noted that you can do what you want, so I will relicense under GPLv3

# oeminfo unpacker for huawei
#   Some code from this file is copyright (C) 2019 Hackintosh5
#   Thanks to rysmario 2016, no copyright asserted by them.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
import sys
import os
import argparse
import zipfile
import tempfile
from struct import *

elements = {
    6: {
        0x12: "Region",
        0x43: "Root Type (info)",
        0x44: "rescue Version",
        0x4a: "16 byte string 0 terminated",
        0x4e: "Rom Version",
        0x58: "Alternate ROM Version?",
        0x5e: "OEMINFO_VENDER_AND_COUNTRY_NAME_COTA",
        0x5b: "Hardware Version Customizeable",
        0x5c: "USB Switch?",
        0x61: "Hardware Version",
        0x62: "PRF?",
        0x65: "Rom Version Customizeable",
        0x67: "CN or CDMA info 0x67",
        0x68: "CN or CDMA info 0x68",
        0x6a: "CN or CDMA info 0x6a",
        0x6b: "CN or CDMA info 0x6b",
        0x6f: "Software Version",
        0x73: "Oeminfo Gamma",
        0x76: "pos_delivery constant",
        0x8b: "Unknown SHA256 1",
        0x85: "3rd_recovery constant",
        0x8c: "Software Version as CSV",
        0x8d: "Unknown SHA256 2",
        0x96: "Unknown SHA256 3",
        0xa6: "Update Token",
        0xa9: "Some kind of json changelog",
        0x15f: "Logo Boot",
        0x160: "Logo Battery Empty",
        0x161: "Logo Battery Charge",
    },
    8: {
        0x5c: "Userlock",
        0x5d: "System Lock State",
        0x28: "Version number",
        0x33: "Software Version as CSV",
        0x35: "semicolon separated text containing device identifiers, possibly used in bootloader code generation",
        0x3f: "update token",
        0x50: "cust version",
        0x52: "preload version",
        0x56: "system version",
        0x5ec: "build number",
        0x5ee: "model number",
        0xc: "system security data",
        0x1197: "Logo Battery Charge",
        0x1196: "Logo Battery Empty",
        0x1196: "Logo additional (custom format)",
        0x1195: "Logo Google",
    }
}

def element(version, key):
    return elements.get(version, {}).get(key, "")

def sanitize_filename(filename):
    # Remove characters not allowed in Windows filenames
    return "".join(c for c in filename if c not in "\\/:*?\"<>|")

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def unpackOEM(f, outdir=None):
    if outdir is None:
        HW_Version = b""  # 61
        HW_Region = b""  # 12
        SW_Version = b""  # 4e

    binary = f.read()
    content_length = len(binary)
    content_startbyte = 0

    if content_length != 67108864:
        print("Wrong filesize")
        return

    while content_startbyte < content_length:
        (header, version_number, id, type, data_len, age) = unpack("8sIIIII", binary[content_startbyte:content_startbyte+0x1c])
        
        if header == b"OEM_INFO":
            if version_number == 6 or version_number == 8:
                if id == 0x61:
                    HW_Version = binary[content_startbyte+0x200:content_startbyte+0x200+data_len]
                if id == 0x12:
                    HW_Region = binary[content_startbyte+0x200:content_startbyte+0x200+data_len]
                if id == 0x4e:
                    SW_Version = binary[content_startbyte+0x200:content_startbyte+0x200+data_len]

                if outdir is not None:
                    ensure_directory_exists(outdir)
                    
                    fileout = "{:x}-{:x}-{:x}-{:x}".format(id, type, age, content_startbyte)
                    
                    try:
                        header_decoded = header.decode('utf-8', errors='replace')
                        print(f"hdr:{header_decoded:<8} age:{age:3x} id:{id:5x} {element(version_number, id)} ")
                    except UnicodeDecodeError:
                        header_decoded = "unknown_header"
                        print(f"hdr:{header_decoded:<8} age:{age:3x} id:{id:5x} {element(version_number, id)} ")
                        
                    with open(os.path.join(outdir, fileout + ".bin"), "wb") as out_file:
                        out_file.write(binary[content_startbyte+0x200:content_startbyte+0x200+data_len])
                    
                    if element(version_number, id):
                        sanitized_filename = sanitize_filename(element(version_number, id))
                        symlink_link = os.path.join(outdir, f"{sanitized_filename}.{hex(content_startbyte)}.txt")
                        with open(symlink_link, "w") as link_file:
                            link_file.write(os.path.join(outdir, fileout + ".bin"))
                    
                    if (version_number == 6 and type == 0x1fa5) or (version_number == 8 and (type == 0x2399 or type == 0x1fa5)):
                        if element(version_number, id):
                            bmp_link = os.path.join(outdir, f"{sanitized_filename}.{hex(content_startbyte)}.bmp")
                            with open(bmp_link, "w") as bmp_file:
                                bmp_file.write(os.path.join(outdir, fileout + ".bin"))
        
        content_startbyte += 0x400
    
    if outdir is None:
        try:
            outdir = sanitize_filename(HW_Version.decode('utf-8').strip()) + "#" + sanitize_filename(HW_Region.decode('utf-8').replace("/", "-").strip()) + "#" + sanitize_filename(SW_Version.decode('utf-8').split('\0', 1)[0].strip())
        except UnicodeDecodeError:
            outdir = "unknown_oeminfo"
        
        ensure_directory_exists(outdir)
        f.seek(0, 0)
        unpackOEM(f, outdir)
    
    return outdir

def encodeOEM(in_folder, out_filename):
    out = bytearray(b'\x00'*0x4000000)
    counter = 0
    content_startbytes = []
    
    for root, subFolder, files in os.walk(in_folder):
        for item in files:
            if item.endswith(".bin"):
                id, type, age, content_startbyte = item.split(".")[0].split("-")
                buf_start = int(content_startbyte, 16)
                with open(os.path.join(root, item), "rb") as infile:
                    data = infile.read()
                    content_length = len(data)
                    if int(id, 16) in (0x69, 0x57, 0x44):
                        out[buf_start-0x1000:buf_start] = b'\xff'*0x1000
                    if int(type, 16) != 0x1fa5 or (int(id, 16) == 0x15f and int(age, 16) > 1) and (int(id, 16) not in (0x160, 0x161)):
                        data += b'\0'*(0x400 - (content_length % 0x400))
                    if int(id, 16) == 0x43 and int(type, 16) == 0x3:
                        data += b'\0'*(0x800 - len(data))
                    out[buf_start:buf_start+len(data)] = data
    
    with open(out_filename, "wb") as f:
        f.write(out)

def replaceOEM(in_folder, out_filename):
    with open(out_filename, "r+b") as f:
        for root, subFolder, files in os.walk(in_folder):
            for item in files:
                if item.endswith(".bin"):
                    id, type, age, content_startbyte = item.split(".")[0].split("-")
                    buf_start = int(content_startbyte, 16)
                    with open(os.path.join(root, item), "rb") as infile:
                        data = infile.read()
                        content_length = len(data)
                        if int(id, 16) in (0x69, 0x57, 0x44):
                            f.seek(buf_start-0x1000)
                            f.write(b'\xff'*0x1000)
                        f.seek(buf_start)
                        f.write(data)

def main():
    parser = argparse.ArgumentParser(description="OEMINFO Tool for Huawei")
    subparsers = parser.add_subparsers(dest='command')
    
    parser_decode = subparsers.add_parser('decode', help='Decode OEMINFO image')
    parser_decode.add_argument('input', type=str, help='Input OEMINFO image file')
    
    parser_encode = subparsers.add_parser('encode', help='Encode to OEMINFO image')
    parser_encode.add_argument('input', type=str, help='Input folder with .bin files')
    parser_encode.add_argument('output', type=str, help='Output OEMINFO image file')
    
    parser_replace = subparsers.add_parser('replace', help='Replace OEMINFO image with folder')
    parser_replace.add_argument('input', type=str, help='Input folder with .bin files')
    parser_replace.add_argument('output', type=str, help='Existing OEMINFO image file')

    args = parser.parse_args()
    
    if args.command == 'decode':
        with open(args.input, 'rb') as f:
            outdir = unpackOEM(f)
            if outdir:
                print(f"Decoded OEMINFO to folder: {outdir}")
    
    elif args.command == 'encode':
        encodeOEM(args.input, args.output)
        print(f"Encoded folder {args.input} to OEMINFO image: {args.output}")
    
    elif args.command == 'replace':
        replaceOEM(args.input, args.output)
        print(f"Replaced OEMINFO data in {args.output} with folder: {args.input}")

if __name__ == "__main__":
    main()

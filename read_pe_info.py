#!/usr/bin/python3

import io
import os
import sys
import pycdlib
import tempfile
import shutil
import pefile

from pycabfile import CabFile

import argparse
import datetime

import subprocess

def read_timestamp_from_file(filename):
    pe = pefile.PE(filename)
    
    pe_headers_dict = pe.FILE_HEADER.dump_dict()
    optional_headers = pe.OPTIONAL_HEADER.dump_dict()

    try:
        res_string = pe.DIRECTORY_ENTRY_RESOURCE
        resource_timestamp = res_string.struct.TimeDateStamp    
    except AttributeError:
        resource_timestamp = 0

    pe_timestamp = int(pe_headers_dict['TimeDateStamp']['Value'].split(' ')[0], 16)
    return (datetime.datetime.fromtimestamp(pe_timestamp), datetime.datetime.fromtimestamp(resource_timestamp))

def extract_cabs_from_cd(iso_name):
    cab_folder_dir = tempfile.mkdtemp()

    iso = pycdlib.PyCdlib()
    iso.open(iso_name)

    files_to_extract = []

    for dirname, dirlist, filelist in iso.walk(iso_path='/'):
        for file in filelist:
            _, file_extension = os.path.splitext(file)
            if (file_extension == '.CAB') or file_extension == '.CAB;1' :
                files_to_extract.append(os.path.join(dirname, file))

    # Copy out all cabinets for cabextract
    for file in files_to_extract:
        filepath, filename = os.path.split(file)
        file_base, file_extension = os.path.splitext(filename)

        if file_extension == '.CAB;1':
            iso.get_file_from_iso(os.path.join(cab_folder_dir, file_base+".CAB"), iso_path=file)
        else:
            iso.get_file_from_iso(os.path.join(cab_folder_dir, filename), iso_path=file)

    iso.close()
    return cab_folder_dir

def extract_cabs_from_floppy(floppy_images):
    cab_folder_dir = tempfile.mkdtemp()

    for floppy in floppy_images:
        # this is horrible, just using mtools because its the least bad option
        subprocess.run(['mcopy', '-i', floppy, '::*.CAB', cab_folder_dir])

    return cab_folder_dir

def main():
    cab_folder_dir = None

    parser = argparse.ArgumentParser(
        prog='Reads PE header info from Windows 9x install media')
    parser.add_argument("-f", "--floppy", type=bool, default=False, help="Extract images from floppy disks")
    parser.add_argument("-c", "--cdrom", type=bool, default=False, help="Extract info from CD image")
    parser.add_argument('filename', nargs='*', help='file to examine')
    args = parser.parse_args()

    if args.cdrom:
        cab_folder_dir = extract_cabs_from_cd(args.filename[0])

    if args.floppy:
        cab_folder_dir = extract_cabs_from_floppy(args.filename)

    # We now need to extract each of the cabinets with cabextract via a subprocess
    # as the pure Python CAB implementation dies horribly on multipart cabinets
    #
    # We need to extract WIN95_02.CAB directly as its the first cabinet file with
    # windows itself; if we extract PRECOPY1, which is technically the first cab
    # in the mediaset, it doesn't pull everything out. Ugh

    # Ok, we need to do a stupid fix here, because the Win95 cabinet name is not
    # the same across all media, we need to determine what the lowest file is, and
    # use that instead
    lowest_win95_cab = None
    for dirname, dirlist, filelist in os.walk(cab_folder_dir):
        for file in filelist:
            if 'WIN95_' in file:
                current_file = int(file.strip("WIN95_").rstrip(".CAB"))
                if lowest_win95_cab is None:
                    lowest_win95_cab = current_file
                if lowest_win95_cab > current_file:
                    lowest_win95_cab = current_file


    extract_dir = tempfile.mkdtemp()
    subprocess.run(['cabextract', '-d'+extract_dir, os.path.join(cab_folder_dir, "WIN95_"+str(lowest_win95_cab).zfill(2)+".CAB")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("Filename, CAB Time, PE Header Time, Resource Timestamp")
    for dirname, dirlist, filelist in os.walk(extract_dir):
        for file in filelist:
            try:
                # cabextract writes the file out to the filesystem with the original metadata
                # so lets grab that and compare
                cab_timestamp = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(extract_dir, file)))
                timestamps = read_timestamp_from_file(os.path.join(extract_dir, file))
                print(f"{file},{cab_timestamp},{timestamps[0]},{timestamps[1]}")
            except pefile.PEFormatError:
                pass


    # delete temp directory
    shutil.rmtree(cab_folder_dir)
    shutil.rmtree(extract_dir)




if __name__ == '__main__':
    main()
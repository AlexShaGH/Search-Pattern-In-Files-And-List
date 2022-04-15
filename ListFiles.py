# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 13:57:49 2022

@author: ALEX SHASHKOV
"""
import sys
import os.path 
import mmap
from datetime import datetime

def log_msg(msg, log, echo=True):
    """
    Logs and prints message 

    Parameters
    ----------
    msg : str
        message to log and print
    log : file object
        app log file
    echo : BOOL, optional
        to print or not. The default is True.

    Returns
    -------
    None.

    """
    entry = '{}: {}\n'.format(datetime.now().strftime("%D:%H:%M:%S"),msg)
    log.write(entry)
    if echo:
        print(entry)
    return

def process_directory(src, np_log, p_log, app_log):
    """
    Recursively processes directory

    Parameters
    ----------
    src : string
         represents path - i.e. E:\director
    np_log : file object
        log file to save names of the files with no found pattern
    p_log : file object
        log file to save names of the files with found pattern
    app_log : file object
        application log file to save events

    Returns
    -------
    None.

    """
    for path, dirs, files in os.walk(src): 
        for file in files:
            process_file(os.path.join(path, file), np_log, p_log, app_log, pattern)
        for directory in dirs:
            process_directory(os.path.join(path, directory), np_log, p_log, app_log)
    return


def process_file(file, not_found_log, found_log, app_log, pattern_signature):
    """
    Opens memory maping of the file and searches in it for pattern
    updates logs and counter accordingly

    Parameters
    ----------
    file : string
        full name of the file
    not_found_log : file object
        log file to save names of the files with no found pattern
    found_log : file object
        log file to save names of the files with found pattern
    app_log : file object
        application log file to save events
    pattern_signature : binary string
        pattern to search in the file

    Returns
    -------
    None.

    """
    found = False
    global bytes_processed
    global files_processed
    global files_found
    try:
        file_size = os.stat(file).st_size
        if file_size > 0:
            with open(file, mode='rb+') as f:
                mm = mmap.mmap(f.fileno(), 0)
                if mm.find(pattern_signature) != -1:
                    found = True
                mm.close()
        if found:
           found_log.write(file+","+str(file_size)+'\n')
           files_found += 1
        else:
           not_found_log.write(file+","+str(file_size)+'\n')
        bytes_processed += file_size
        files_processed += 1
        #output_stream.write("processed {0:,} files in {1:,} bytes, found pattern in {2:,} files \r".format(files_processed,bytes_processed,files_found))           
        output_stream.write("processed {0:,} files, found pattern in {1:,} files \r".format(files_processed,files_found))           
    except Exception as e:
        msg = "Unable to process file: {0}, exception: {1}".format(file,e)
        log_msg(msg, app_log)
        
    return

output_stream = sys.stdout
bytes_processed = 0
files_processed = 0
files_found = 0
pattern = bytes('Data Recovery Labs','ascii')# default search pattern

def main():
    # check and parse arguments
    global pattern
    args = sys.argv[1:]
    arg_cnt = len(args)
    if arg_cnt < 2 or arg_cnt>3:
        print("arguments count is incorrect!")
        print("Expecting 2 or 3: ['src_path', 'dst_path', 'srch_pattern'(optional)] but received {0}: {1}".format(len(args),args))
        print("Usage: ListFile.py <src_path> <dst_path> <srch_pattern(optional)>")
        print("Where: src_path = source directory, dst_path = directory for logs, , srch_pattern = string to search in files")
        print('Example: python ListFiles.py E:\ C:\JOBS "Data Recovery Labs"')
        return
    elif arg_cnt == 3:
        pattern = bytes(args[2],'ascii')
    src_path = args[0]
    if not os.path.isdir(src_path):
        print("Source path {0} does not exists".format(src_path))
        return
    dst_path = args[1]
    if not os.path.isdir(dst_path):
        print("Destination path {0} does not exists".format(dst_path))
    
    # create destination logs
    with open(os.path.join(dst_path, "log.txt"), "w",encoding="utf-8") as app_log_file,open(
        os.path.join(dst_path, "files_no_pattern.txt"), "w",encoding="utf-8") as files_np_log,open(
        os.path.join(dst_path, "files_with_pattern.txt"), "w",encoding="utf-8") as files_p_log:
            
            log_msg("ListFiles.py: Application started", app_log_file)
            log_msg("Source directory path: {}".format(src_path), app_log_file)    
            log_msg("Destination path for the lists: {}".format(dst_path), app_log_file)
    
            log_msg("Processing data", app_log_file)
            # Loop through the directories recursively and check files
            process_directory(src_path, files_np_log, files_p_log, app_log_file)
            # update logs with totals
            files_np_log.write('Total: {:,}'.format(files_processed-files_found)+'\n')
            files_p_log.write('Total: {:,}'.format(files_found)+'\n')
            log_msg("Processed {0:,} bytes in {1:,} files, found {2:,} files with pattern".format(
                bytes_processed,files_processed,files_found), app_log_file)     

            log_msg("Done", app_log_file)     
    
if __name__ == "__main__":
    main()
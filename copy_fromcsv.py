import argparse
from distutils.log import info
import os
import logging as log
import socket
import getpass
import sys
import pandas as pd
import subprocess

FORMAT = '%(asctime)s %(clientip)-15s %(user)-8s %(message)s'
ROOT_DIR = os.path.realpath(os.path.dirname(__file__))


def fix_path(path_name, must_exist=True):
    # os separator
    fixed_path = os.path.normpath(path_name)

    # real or relative
    if os.path.exists(fixed_path) \
        or os.path.exists(os.path.join(ROOT_DIR, fixed_path)) \
        or not must_exist:
        return fixed_path
    return None


def main(csv, src, dst, out):
    folders = pd.read_csv(csv, names=['folders'], header=None)
    with open(out, 'a') as log_file:
        for _, raw_folder in folders.iterrows():
            # prefix each relative folder by source and destination
            raw_folder = raw_folder.iloc[0] # convert from series to scalar
            src_folder = fix_path(
                os.path.join(src, raw_folder))
            dst_folder = fix_path(
                os.path.join(dst, raw_folder),
                must_exist=False)
            if not src_folder:
                logger.warning('Skipped Path: %s', raw_folder, extra=d)
                continue
            logger.info('Copy Path: %s', raw_folder, extra=d)
            # ensure the destination does exist
            if not os.path.exists(dst_folder):
                os.makedirs(dst_folder)
            # copy
            output = subprocess.run(['robocopy',
                src_folder,
                dst_folder,
                '/mir', '/eta', '/tee', '/mt:32'],
                capture_output=True,
                text=True)
            log_file.writelines(output.stdout)
            logger.info('Done Path: %s', raw_folder, extra=d)


if __name__ == "__main__":
    # create parameters
    parser = argparse.ArgumentParser(description='Copy From CSV')
    parser.add_argument('--csv', dest='csvPath', type=str, help='Path of the CSV file', required=True)
    parser.add_argument('--src', dest='srcPath', type=str, help='Path of the source directory', required=True)
    parser.add_argument('--dest', dest='dstPath', type=str, help='Path of the destination directory', required=True)
    parser.add_argument('--log', dest='outPath', type=str, help='Path of the log file', required=True)
    args = parser.parse_args()

    # init logger
    log.basicConfig(format=FORMAT, level=log.INFO)
    d = {
        'clientip': socket.gethostbyname(socket.getfqdn()), 
        'user': getpass.getuser()}
    logger = log.getLogger('copy_fromcsv')
    logger.info('CSV Path: %s', args.csvPath, extra=d)
    logger.info('Source Path: %s', args.srcPath, extra=d)
    logger.info('Destination Path: %s', args.dstPath, extra=d)
    logger.info('Log Path: %s', args.outPath, extra=d)
    
    # fix parameters
    csv = fix_path(args.csvPath)
    src = fix_path(args.srcPath)
    dst = fix_path(args.dstPath, must_exist=False)
    out = fix_path(args.outPath, must_exist=False)
    
    # verify parameters
    if not csv:
        logger.error('CSV Path: %s', 'not found!', extra=d)
        sys.exit('CSV Path: %s' % 'not found!')
    if not src:
        logger.error('Source Path: %s', 'not found!', extra=d)
        sys.exit('Source Path: %s' % 'not found!')
    if not os.path.exists(dst):
        os.makedirs(dst)
    
    # run main
    main(csv, src, dst, out)

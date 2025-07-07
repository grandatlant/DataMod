#!/usr/bin/env -S python3 -O
# -*- coding = utf-8 -*-
r"""Script for MPQ patch file creation, using external utility smpq:
sudo apt install smpq

Or you can try to get it here:
https://code.launchpad.net/smpq

Or use manuals from here:
https://github.com/bubio/smpq
https://www.zezula.net/en/mpq/download.html#StormLib
"""

__version__ = '0.0.1'
__copyright__ = 'Copyright (C) 2025 grandatlant'

# Global defaults
patch_name = 'patch-Y.MPQ'
patch_content = [
    'Creature',
    'Fonts',
    'Sound',
]

import os
import subprocess
from argparse import ArgumentParser

import logging
logging.basicConfig(
    level = logging.DEBUG if __debug__ else logging.ERROR,
    style = '{',
    format = '{levelname}::{message}'
)
log = logging.getLogger(__name__)

# I do not support Windows users, but lets give it a shot.
# You can override it if you want to change SMPQ system command prefix
# or use another utility
smpq_cmd = ['smpq'] if os.name == 'posix' else [r'C:\smpq\build\smpq.exe']


def init_patch(name: str):
    command = [
        *smpq_cmd,
        '--create',
        '--mpq-version',
        '2',
        '--force',
        '--verbose',
        '"%s"' % name if ' ' in name else name,
    ]
    print(f'Patch "%s", init: ' % name, *command)
    result = subprocess.run(
        command,
        text=True,
        #check=True,
        capture_output=True,
    )
    if result.stdout:
        print(f'Init STDOUT:\n{result.stdout}')
    if result.stderr:
        print(f'Init STDERR:\n{result.stderr}')
    print(f'Patch "%s" init finished. Return code:' % name, result.returncode)
    return result.returncode or 0


def append_files(patch: str, files: list) -> int:
    command = [
        *smpq_cmd,
        '--append',
        '--verbose',
        patch,
        *files,
    ]
    print(f'Patch "%s", append files.' % patch)
    result = subprocess.run(
        command,
        text=True,
        #check=True,
        capture_output=True,
    )
    if result.stdout:
        print(f'Append STDOUT:\n{result.stdout}')
    if result.stderr:
        print(f'Append STDERR:\n{result.stderr}')
    print(f'Patch "%s" append finished. Return code:' % patch, result.returncode)
    return result.returncode or 0


def list_dir_files(dirname: str) -> list:
    files = []
    for dirpath, dirnames, filenames in os.walk(dirname):
        for filename in filenames:
            name = os.path.join(dirpath, filename)
            files.append('"%s"' % name if ' ' in name else name)
    return files


def append_patch(name: str, content: list) -> int:

    # status code gathering variable
    append_result = int()
    for item in content:
        log.debug('Processing content item "%s".', item)
        if os.path.isfile(item):
            print(f'Append file "{item}".')
            append_result |= append_files(name, [item])
        elif os.path.isdir(item):
            print(f'Append ALL files from dir "{item}" (recursive).')
            append_result |= append_files(name, list_dir_files(item))
        else:
            log.warning('Item "%s" is not file nor directory. Skip.', item)
    else:
        log.debug('Content processing finished in full. Content: %s', content)
    
    return append_result


def parse_cli_args(args=None):
    
    parser = ArgumentParser(
        description = __doc__,
        allow_abbrev = False,
        epilog = __copyright__,
    )
    
    parser.add_argument(
        '-v',
        '--version',
        action = 'version',
        version = f'%(prog)s {__version__}',
    )
    parser.add_argument(
        '-p',
        '--patch',
        default = patch_name,
        help = f'''name for new MPQ archive. 
        Default filename "{patch_name}" script-defined.''',
    )
    parser.add_argument(
        '-a',
        '--append',
        action = 'store_true',
        default = False,
        help = f'''append existing patch file.
        New force-created by default.''',
    )
    parser.add_argument(
        'content',
        nargs = '*',
        default = patch_content,
        help = f'''name of directories or files to pack.
        Default content "{patch_content}" script-defined.''',
    )
    
    return parser.parse_args()


##  MAIN ENTRY POINT
def main(args=None):
    args = parse_cli_args(args)
    log.debug('Parsed args: {args}'.format(args=args))
    
    if args.content:
        if not args.append or not os.path.exists(args.patch):
            # init new file first
            if init_result := init_patch(args.patch):
                log.error('init_patch() error. Status code: %i.', init_result)
                return init_result
        
        if append_result := append_patch(args.patch, args.content):
            log.error('append_files() error. Status code: %i.', append_result)
            return append_result
    
    log.debug('main() OK. return 0')
    return 0


if __name__ == '__main__':
    main()

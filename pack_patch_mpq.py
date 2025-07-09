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

__version__ = '0.0.3'
__copyright__ = 'Copyright (C) 2025 grandatlant'

import os
import sys
import subprocess
from argparse import ArgumentParser

import logging
logging.basicConfig(
    level = logging.DEBUG if __debug__ else logging.ERROR,
    stream = sys.stdout,
    style = '{',
    format = '{levelname}::{message}'
)
log = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*a, **k):
        log.warning('load_dotenv() call with missing python-dotenv.')
load_dotenv()

# Global defaults
PATCH_NAME = 'patch-Y.MPQ'
PATCH_CONTENT = [
    'Creature',
    'Fonts',
    'Sound',
]
# I do not support Windows users, but lets give it a shot.
# You can override it if you want to change SMPQ system command prefix
# or use another utility
SMPQ_CMD = 'smpq' if os.name == 'posix' else r'C:\smpq\build\smpq.exe'
smpq = os.getenv('SMPQ', SMPQ_CMD)


def init_patch(name: str, mpq_version: str = '2') -> int:
    """Creates new MPQ file witn given "name" and "version" using smpq util.
    Return value: status code returned by smpq."""
    command = [
        smpq,
        '--create',
        '--mpq-version',
        str(mpq_version),
        '--force',
        '--verbose',
        name,
    ]
    log.info('Patch "%s", init: %s', name, command)
    result = subprocess.run(
        command,
        text=True,
        #check=True,
        capture_output=True,
    )
    if result.stdout:
        log.info('Output:\n%s', result.stdout)
    if result.stderr:
        log.info('Errors:\n%s', result.stderr)
    log.info('Patch "%s" init finished. Return code: %i',
             name, result.returncode)
    return result.returncode or 0


def append_files(patch: str, files: list) -> int:
    """Append existing MPQ file "patch"
    with list of "files" given using smpq util.
    Return value: status code returned by smpq."""
    command = [
        smpq,
        '--append',
        '--force',
        '--verbose',
        patch,
        *files,
    ]
    log.info('Patch "%s", append files.', patch)
    result = subprocess.run(
        command,
        text=True,
        #check=True,
        capture_output=True,
    )
    if result.stdout:
        log.info('Output:\n%s', result.stdout)
    if result.stderr:
        log.info('Errors:\n%s', result.stderr)
    log.info('Patch "%s" append finished. Return code: %i',
             patch, result.returncode)
    return result.returncode or 0


def list_dir_files(dirname: str) -> list:
    """os.walk directory named "dirname"
    and form a list of all files in it 
    with relative dirpath included to each filename.
    Return value: list of strings representing filenames."""
    files = list()
    for dirpath, dirnames, filenames in os.walk(dirname):
        for filename in filenames:
            files.append(os.path.join(dirpath, filename))
    return files


def append_patch(name: str, content: list) -> int:
    """Append files listed in "content"
    to MPQ archive named "name".
    Return value: int - combination (bitwise OR) of return codes,
    returned by smpq utility while executing append_files() calls."""
    # status code gathering variable
    append_result = int()
    for item in content:
        log.debug('Processing content item "%s".', item)
        if os.path.isfile(item):
            log.info('Append file "%s".', item)
            append_result |= append_files(name, [item])
        elif os.path.isdir(item):
            log.info('Append files from dir "%s" (recursive).', item)
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
        '-a',
        '--append',
        action = 'store_true',
        default = False,
        help = '''append existing patch file. 
        New force-created by default or if not exists.''',
    )
    parser.add_argument(
        '-p',
        '--patch',
        default = PATCH_NAME,
        help = f'''MPQ archive name. 
        Default filename "{PATCH_NAME}" script-defined.''',
    )
    parser.add_argument(
        'content',
        nargs = '*',
        default = PATCH_CONTENT,
        help = f'''name of directories or files to pack.
        Default content "{PATCH_CONTENT}" script-defined.''',
    )
    return parser.parse_args(args)


##  MAIN ENTRY POINT
def main(args=None):
    if args is sys.argv:
        args = args[1:]
    parsed = parse_cli_args(args)
    log.debug('Parsed args: %s', parsed)
    
    if parsed and parsed.content:
        if not parsed.append or not os.path.exists(parsed.patch):
            # init new file first
            if init_result := init_patch(parsed.patch):
                log.error('init_patch() error. Status code: %i.', init_result)
                return init_result
        # now append existing patch
        if append_result := append_patch(parsed.patch, parsed.content):
            log.error('append_files() error. Status code: %i.', append_result)
            return append_result
    
    log.debug('main() OK. return 0')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

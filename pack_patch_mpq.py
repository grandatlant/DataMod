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

__version__ = '0.0.6'
__copyright__ = 'Copyright (C) 2025 grandatlant'

import os
import sys
import subprocess
from argparse import ArgumentParser, Namespace

from typing import (
    Optional, Union,
    List, Dict,
)

import logging
logging.basicConfig(
    level = logging.DEBUG if __debug__ else logging.INFO,
    stream = sys.stdout,
    style = '{',
    format = '{levelname}::{message}',
)
log: logging.Logger = logging.getLogger(__name__)

# Global defaults
PATCH_NAME = 'patch-Y.MPQ'
PATCH_CONTENT = [
    'Creature',
    'Fonts',
    'Sound',
]
# Lets give a try to Windows users use this script.
SMPQ_CMD = 'smpq' if os.name == 'posix' else r'C:\smpq\build\smpq.exe'
# You can override it with SMPQ variable in your environment
# or .env file value 'SMPQ'
dotENV: Dict[str, Optional[str]] = {
    'SMPQ': None,
}
try:
    from dotenv import dotenv_values
    dotENV.update(dotenv_values())
except ImportError:
    # pip install python-dotenv
    log.warning('python-dotenv is missing, using defaults.')

smpq: str = os.getenv('SMPQ') or dotENV.get('SMPQ') or SMPQ_CMD


def ensure_patch_name(filename: str) -> str:
    """Converts argument to format "patch-XXXX.MPQ" if it is not.
    Return value: str - converted value or argument itself."""
    if not filename.lower().startswith('patch-'):
        filename = 'patch-' + filename
    if not filename.upper().endswith('.MPQ'):
        filename += '.MPQ'
    return filename


def init_patch(name: str, mpq_version: Union[str, int] = '2') -> int:
    """Creates new MPQ file with given "name" and "version" using smpq util.
    MPQ Version 2 used by default for World of Warcraft: Wrath of the Lich King.
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
        log.error('Errors:\n%s', result.stderr)
    log.info(
        'Patch "%s" init finished. Return code: %x',
        name,
        result.returncode,
    )
    return result.returncode or 0


def append_files(patch: str, files: List[str]) -> int:
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
    log.info('Patch "%s", append files...', patch)
    result = subprocess.run(
        command,
        text=True,
        #check=True,
        capture_output=True,
    )
    if result.stdout:
        log.info('Output:\n%s', result.stdout)
    if result.stderr:
        log.error('Errors:\n%s', result.stderr)
    log.info(
        'Patch "%s" append finished. Return code: %x',
        patch,
        result.returncode,
    )
    return result.returncode or 0


def list_dir_files(dirname: str) -> List[str]:
    """os.walk directory named "dirname"
    and form a list of all files in it 
    with relative dirpath included to each filename.
    Return value: list of strings representing filenames."""
    files = list()
    for dirpath, dirnames, filenames in os.walk(dirname):
        for filename in filenames:
            files.append(os.path.join(dirpath, filename))
    return files


def append_patch(name: str, content: List[str]) -> int:
    """Append files listed in "content"
    to MPQ archive named "name".
    Return value: int - combination (bitwise OR) of return codes,
    returned by smpq utility while executing append_files() calls."""
    # status code gathering variable
    append_result = int(0)
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


def parse_cli_args(args: Optional[List[str]] = None) -> Namespace:
    
    parser: ArgumentParser = ArgumentParser(
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
        help = f'''MPQ archive name in format "patch-X.MPQ" or just "X".
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
def main(args: Optional[List[str]] = None) -> int:
    if args is sys.argv:
        args = args[1:]
    parsed: Namespace = parse_cli_args(args)
    log.debug('Parsed args: %s', parsed)
    
    patch: str = ensure_patch_name(parsed.patch)
    if not parsed.append or not os.path.exists(patch):
        # init new patch file first
        if init_result := init_patch(patch):
            log.error(
                'init_patch(%s) error. Status code: %x.',
                patch,
                init_result,
            )
            return init_result
    
    # now append existing patch
    if append_result := append_patch(patch, parsed.content):
        log.error(
            'append_patch(%s, ...) error. Status code: %x.',
            patch,
            append_result,
        )
        return append_result
    
    log.debug('main(%s) OK. return 0', args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

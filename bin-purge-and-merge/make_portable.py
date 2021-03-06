#!/usr/bin/env python
'''
Usage: make_portable.py [OPTIONS] SRC DST

  Create a wrapper (DST) for a binary file/program (SRC) by copying and
  wrapping all the neccesary files as a new portable project that can be 
  run on another computer.

Options:
  -s, --symlink   Will make symlinks and not file-copies, good for testing.
  -l, --lib TEXT  List of library files (usually .so) to be copied and linked
                  to. Seperate multiple files as -l file1 -l file2 ...
  --help          Show this message and exit.
'''

import subprocess
import os
import errno
import click
import shutil

binwrap_template = r'''#!/bin/bash

#--------------------------------------------------
# I might be a symlink, so here is my root dwelling
#--------------------------------------------------

#From https://stackoverflow.com/a/246128
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" 
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

#--------------------------------------------------
# Hey linker, also look here for .so files
#--------------------------------------------------

#From https://stackoverflow.com/a/37558191
export LD_LIBRARY_PATH=$DIR/bin:$LD_LIBRARY_PATH

#--------------------------------------------------
# Finally, hey Linux, run this binary please
#--------------------------------------------------

"$DIR/bin/%s" "$@"
'''

def make_runner(src, dst, do_ln=False):
    wrap_dir, wrap_name = os.path.split(dst)
    blob_path = wrap_dir+'/bin/'+wrap_name

    cp(src, blob_path, do_ln=do_ln)

    with open(dst, 'w') as f:
        f.write(binwrap_template%(wrap_name))

    #make dest wrapper executable
    subprocess.call(['chmod', '+x', dst])


def cp(src, dst, do_ln=False):
    dstdir = os.path.dirname(dst)

    try:
        os.remove(dst)
    except:
        pass

    os.makedirs(dstdir, exist_ok=True)

    if do_ln:
        subprocess.call(["ln", src, dst, "-s"])
    else:
        shutil.copy2(src, dst)


@click.command()
@click.argument(
    'src',
    required=True,
    type=(click.Path(exists=True))
)
@click.argument(
    'dst',
    required=True,
    type=(click.Path())
)
@click.option(
    '--symlink',
    '-s',
    is_flag=True,
    help='Will make symlinks and not file-copies, good for testing.'
)
@click.option(
    '--lib',
    '-l',
    multiple=True,
    help='List of library files (usually .so) to be copied and linked to. '
         'Seperate multiple files as -l file1 -l file2 ...'
)
def runner(src, dst, symlink, lib):
    """Create a wrapper (DST) for a binary file/program (SRC) by copying and wrapping all
    the neccesary files as a new portable project that can be run on another computer."""

    dst = os.path.abspath(dst)
    wrap_dir, _ = os.path.split(dst)

    make_runner(src, dst, do_ln=symlink)
    for l in lib:
        l = os.path.abspath(l)
        _, lib_name = os.path.split(l)
        cp(l, wrap_dir+'/bin/'+lib_name, do_ln=symlink)

if __name__ == "__main__":
    runner()
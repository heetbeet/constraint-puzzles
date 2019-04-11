import subprocess
import os
import errno

this_dir = os.path.split(os.path.abspath(__file__))[0]
os.chdir(this_dir)


def make_runner(filepath):
    os.makedirs('bin', exist_ok=True)
    runner_name = os.path.split(filepath)[-1]
    cppbin_name = 'bin/'+runner_name

    #shutils.copy2(filepath, cppbin_name)
    subprocess.call(["ln", filepath, cppbin_name, "-s"])

    open(runner_name, 'w').write(r'''#!/bin/sh
    PROGRAM_DIRECTORY="`dirname "$0"`"
    export LD_LIBRARY_PATH="$PROGRAM_DIRECTORY"

    #chmod +x "$PROGRAM_DIRECTORY/'''+cppbin_name+r'''"
    "$PROGRAM_DIRECTORY/'''+cppbin_name+r'''" "$@"
    ''')

    subprocess.call(['chmod', '+x', runner_name])


os.makedirs('bin', exist_ok=True)
make_runner("/home/simon/devel/eg_emdw/cmake-build-debug/src/eg_ksat")
subprocess.call(["ln", "../../../emdw/build/src/libemdw.so", "bin/.", "-s"])
subprocess.call(["ln", "../../../gLinear/build/Linux-Release-x86_64/libgLinear.so", "bin/.", "-s"])
subprocess.call(["ln", "../../../patrecII/build/Linux-Release-x86_64/lib/libpatrecII.so", "bin/.", "-s"])

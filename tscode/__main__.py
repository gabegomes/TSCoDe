# coding=utf-8
'''

TSCoDe: Transition State Conformational Docker
Copyright (C) 2021-2023 Nicolò Tampellini

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

https://github.com/ntampellini/TSCoDe

Nicolo' Tampellini - nicolo.tampellini@yale.edu

'''

__version__ = '0.3.5'

if __name__ == '__main__':

    import os
    import argparse

    usage = '''python -m tscode [-h] [-s] [-t] inputfile [-n NAME]
        
        positional arguments:
          inputfile               Input filename, can be any text file.

        optional arguments:
          -h, --help              Show this help message and exit.
          -s, --setup             Guided setup of the calculation settings.
          -t, --test              Perform some tests to check the TSCoDe installation.
          -n NAME, --name NAME    Custom name for the run.
          -cl, --command_line     Read instructions from command line instead of from inputfile
          -c, --cite              Print citation links.
          -p, --profile           Profile the run through cProfiler.\n'''

    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument("-s", "--setup", help="Guided setup of the calculation settings.", action="store_true")
    parser.add_argument("-t", "--test", help="Perform some tests to check the TSCoDe installation.", action="store_true")
    parser.add_argument("-cl", "--command_line", help="Read instructions from command line instead of from inputfile.", action="store")
    parser.add_argument("inputfile", help="Input filename, can be any text file.", action='store', nargs='?', default=None)
    parser.add_argument("-n", "--name", help="Custom name for the run.", action='store', required=False)
    parser.add_argument("-c", "--cite", help="Print the appropriate document links for citation purposes.", action='store_true', required=False)
    parser.add_argument("-p", "--profile", help="Profile the run through cProfiler.", action='store_true', required=False)
    args = parser.parse_args()

    if (not (args.test or args.setup or args.command_line)) and args.inputfile is None:
        parser.error("One of the following arguments are required: inputfile, -t, -s.")

    if args.setup:
        from tscode.modify_settings import run_setup
        run_setup()
        quit()

    if args.cite:
        print('No citation link is available for TSCoDe yet. You can link to the code on https://www.github.com/ntampellini/TSCoDe')
        quit()

    if args.test:
        from tscode.tests import run_tests
        run_tests()
        quit()

    if args.command_line:
        
        filename = 'input_TSCoDe.txt'
        with open(filename, 'w') as f:
            f.write(args.command_line)

        args.inputfile = filename

    filename = os.path.realpath(args.inputfile)

    from tscode.embedder import Embedder

    if args.profile:
        from tscode.profiler import profiled_wrapper
        profiled_wrapper(filename, args.name)
        quit()

    # import faulthandler
    # faulthandler.enable()

    embedder = Embedder(filename, stamp=args.name)
    # initialize embedder from input file

    embedder.run()
    # run the program
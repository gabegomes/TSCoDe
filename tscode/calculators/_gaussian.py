# coding=utf-8
'''

TSCODE: Transition State Conformational Docker
Copyright (C) 2021 Nicolò Tampellini

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

'''
from subprocess import DEVNULL, STDOUT, check_call

from cclib.io import ccread
from tscode.settings import COMMANDS, MEM_GB
from tscode.solvents import get_solvent_line
from tscode.utils import clean_directory, pt


def gaussian_opt(coords, atomnos, constrained_indexes=None, method='PM6', procs=1, solvent=None, title='temp', read_output=True):
    '''
    This function writes a Gaussian .inp file, runs it with the subprocess
    module and reads its output.

    :params coords: array of shape (n,3) with cartesian coordinates for atoms.
    :params atomnos: array of atomic numbers for atoms.
    :params constrained_indexes: array of shape (n,2), with the indexes
                                 of atomic pairs to be constrained.
    :params method: string, specifiyng the first line of keywords for the MOPAC input file.
    :params title: string, used as a file name and job title for the mopac input file.
    :params read_output: Whether to read the output file and return anything.
    '''

    s = ''

    if MEM_GB is not None:
        if MEM_GB < 1:
            s += f'%mem={int(1000*MEM_GB)}MB\n'
        else:
            s += f'%mem={MEM_GB}GB\n'

    if procs > 1:
        s += f'%nprocshared={procs}\n'

    s = '# opt ' if constrained_indexes is not None else '# opt=modredundant '
    s += method
    
    if solvent is not None:
        s += ' ' + get_solvent_line(solvent, 'GAUSSIAN', method)
    
    s += '\n\nGaussian input generated by TSCoDe\n\n0 1\n'

    for i, atom in enumerate(coords):
        s += '%s     % .6f % .6f % .6f\n' % (pt[atomnos[i]].symbol, atom[0], atom[1], atom[2])

    s += '\n'

    if constrained_indexes is not None:

        for a, b in constrained_indexes:
            s += 'B %s %s F\n' % (a+1, b+1) # Gaussian numbering starts at 1

    s = ''.join(s)
    with open(f'{title}.com', 'w') as f:
        f.write(s)
    
    try:
        check_call(f'{COMMANDS["GAUSSIAN"]} {title}.com'.split(), stdout=DEVNULL, stderr=STDOUT)

    except KeyboardInterrupt:
        print('KeyboardInterrupt requested by user. Quitting.')
        quit()

    if read_output:

        try:
            data = ccread(f'{title}.out')
            opt_coords = data.atomcoords[0]
            energy = data.scfenergies[-1] * 23.060548867 # eV to kcal/mol

            clean_directory()

            return opt_coords, energy, True

        except FileNotFoundError:
            return None, None, False
# coding=utf-8
'''

TSCODE: Transition State Conformational Docker
Copyright (C) 2021-2023 Nicolò Tampellini

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

'''
import os

import numpy as np

from tscode.settings import (CALCULATOR, DEFAULT_FF_LEVELS, FF_CALC,
                             FF_OPT_BOOL, PROCS, THREADS)
from tscode.utils import read_xyz

keywords_list = [
            'BYPASS',         # Debug keyword. Used to skip all pruning steps and
                                # directly output all the embedded geometries.

            'CALC',           # Manually overrides the calculator in "settings.py"
            
            'CHECK',          # Visualize the input molecules through the ASE GUI,
                                # to check orbital positions or reading faults.

            'CONFS',          # Maximum number of conformers generated by csearch 
                                
            'CLASHES',        # Manually specify the max number of clashes and/or
                                # the distance threshold at which two atoms are considered
                                # clashing. The more forgiving, the more structures will reach
                                # the geometry optimization step. Syntax: `CLASHES(num=3,dist=1.2)`
            
            'DEEP',           # Performs a deeper search, retaining more starting points
                                # for calculations and smaller turning angles.

            'DEBUG',          # DEBUG KEYWORD. Writes more stuff to file.
                                
            'DIST',           # Manually imposed distance between specified atom pairs,
                                # in Angstroms. Syntax uses parenthesis and commas:
                                # `DIST(a=2.345,b=3.67,c=2.1)`

            'ENANTIOMERS',    # Do not discard enantiomeric structures.

            'EZPROT',         # Double bond protection

            'FFOPT',          #Manually turn on ``FF=ON`` or off ``FF=OFF`` the force
                                # field optimization step, overriding the value in ``settings.py``.

            'FFCALC',          # Manually overrides the force field calculator in "settings.py"

            'FFLEVEL',        # Manually set the theory level to be used.
                                # . Syntax: `FFLEVEL=UFF

            'KCAL',           # Trim output structures to a given value of relative energy.
                                # Syntax: `KCAL=n`, where n can be an integer or float.

            'LET',            # Overrides safety checks that prevent the
                                # program from running too large calculations

            'LEVEL',          # Manually set the theory level to be used.
                                # . Syntax: `LEVEL(PM7_EPS=6.15)
                                
            'MTD',            # Run conformational augmentation through metadynamic sampling (XTB)

            'NCI',            # Estimate and print non-covalent interactions present in the generated poses.

            'NEB',            # Perform an automatical climbing image nudged elastic band (CI-NEB)
                                # TS search after the partial optimization step, inferring reagents
                                # and products for each generated TS pose. These are guessed by
                                # approaching the reactive atoms until they are at the right distance,
                                # and then partially constrained (reagents) or free (products) optimizations
                                # are carried out to get the start and end points for a CI-NEB TS search.
                                # For trimolecular transition states, only the first imposed pairing (a) 
                                # is approached - i.e. the C-C reactive distance in the example above.
                                # This NEB option is only really usable for those reactions in which two
                                # (or three) molecules are bound together (or strongly interacting) after
                                # the TS, with no additional species involved. For example, cycloaddition
                                # reactions are great candidates while atom transfer reactions
                                # (i.e. epoxidations) are not. Of course this implementation is not
                                # always reliable, and it is provided more as an experimenting tool
                                # than a definitive feature.

            'NEWBONDS',       # Manually specify the maximum number of "new bonds" that a
                                # TS structure can have to be retained and not to be considered
                                # scrambled. Default is 1. Syntax: `NEWBONDS=1`

            'NOOPT',          # Skip the optimization steps, directly writing structures to file.

            'ONLYREFINED',    # Discard structures that do not successfully refine bonding distances.

            'PKA',            # Set reference pKa for a specific compound

            'PROCS',          # Set the number of parallel cores to be used by ORCA

            'REFINE',            # Same as calling refine> on a single file

            'RIGID',          # Does not apply to "string" embeds. Avoid
                                # bending structures to better build TSs.

            'ROTRANGE',       # Does not apply to "string" embeds. Manually specify the rotation
                                # range to be explored around the structure pivot.
                                # Default is 120. Syntax: `ROTRANGE=120`

            'SADDLE',         # After embed and refinement, optimize to first order saddle points

            'SHRINK',         # Exaggerate orbital dimensions during embed, scaling them by a factor
                                # of one and a half. This makes it easier to perform the embed without
                                # having molecules clashing one another. Then, the correct distance between
                                # reactive atom pairs is achieved as for standard runs by spring constraints
                                # during MOPAC/ORCA optimization.

            'SOLVENT',          # set the solvation model

            'STEPS',          # Manually specify the number of steps to be taken in scanning rotations.
                                # For string embeds, the range to be explored is the full 360°, and the
                                # default `STEPS=24` will perform 15° turns. For cyclical and chelotropic
                                # embeds, the rotation range to be explored is +-`ROTRANGE` degrees.
                                # Therefore, the default value of `ROTRANGE=120 STEPS=12` will perform
                                # twelve 20 degrees turns.

            'SUPRAFAC',       # Only retain suprafacial orbital configurations in cyclical TSs.
                                # Thought for Diels-Alder and other cycloaddition reactions.

            'RMSD',           # RMSD threshold (Angstroms) for structure pruning. The smaller,
                                # the more retained structures. Default is 0.5 A.
                                # Syntax: `RMSD=n`, where n is a number.

            'TS',             # Uses various scans/saddle algorithms to locate the TS

            'THREADS',       # Change the number of maximum concurrent processes (default is 4)
]

class Truthy_struct:
    def __bool__(self):
        return True

class Options:

    rotation_range = 90
    rotation_steps = None # Set later by the _setup() function, based on embed type
    rmsd = None # Set later by the _setup() function, based on embed type/atom number
    rigid = False
    max_confs = 1000
    
    max_clashes = 0
    clash_thresh = 1.5

    max_newbonds = 0

    optimization = True
    calculator = CALCULATOR
    theory_level = None        # set later in _calculator_setup()
    procs = PROCS
    threads = THREADS
    solvent = None
    ff_opt = FF_OPT_BOOL
    ff_calc = FF_CALC

    if ff_opt:
        ff_level = DEFAULT_FF_LEVELS[FF_CALC]

    neb = False
    saddle = False
    ts = False
    nci = False
    shrink = False
    shrink_multiplier = 1
    metadynamics = False
    suprafacial = False
    only_refined = False
    # keep_enantiomers = False
    double_bond_protection = False
    keep_hb = False
    csearch_aug = False

    fix_angles_in_deformation = False
    # Not possible to set manually through a keyword.
    # Monomolecular embeds have it on to prevent
    # scrambling, but better to leave it off for
    # less severe deformations, since convergence
    # is faster

    kcal_thresh = 10
    bypass = False
    debug = False
    let = False
    check_structures = False
    noembed = False
    # Default values, updated if _parse_input
    # finds keywords and calls _set_options

    operators = []
    # this list will be filled with operator strings
    # that need to be exectured before the run. i.e. ['csearch>mol.xyz']

    def __repr__(self):
        d = {var:self.__getattribute__(var) for var in dir(self) if var[0:2] != '__'}
        
        repr_if_true = (
            'bypass',
            'check_structures',
            'debug',
            'let',
            'metadynamics',
            'nci',
            'neb',
            'saddle',
            'ts',
            'ff_opt',
            'noembed',
            'keep_hb',
            'operators',
            'keep_hb',
            # 'operators',
        )
        
        for name in repr_if_true:
            if d.get(name,True):
                d.pop(name)

        repr_if_not_none = (
            'kcal_thresh',
            'solvent',
        )

        for name in repr_if_not_none:
            if d[name] is None:
                d.pop(name)

        if not FF_OPT_BOOL:
            d.pop('ff_calc')

        if self.calculator not in ('ORCA', ' GAUSSIAN'):
            d.pop('procs')

        padding = 1 + max([len(var) for var in d])

        return '\n'.join([f'{var}{" "*(padding-len(var))}: {d[var]}' for var in d])

class OptionSetter:

    def __init__(self, embedder, *args):

        embedder.kw_line = embedder.kw_line if hasattr(embedder, 'kw_line') else ''

        self.keywords = [word.split('=')[0].upper() if not '(' in word
                                else word.split('(')[0].upper()
                                for word in embedder.kw_line.split()]

        self.keywords_simple = [k.upper() for k in embedder.kw_line.split()]
        self.keywords_simple_case_sensitive = embedder.kw_line.split()
        self.embedder = embedder
        self.args = args

        if not all(k in keywords_list for k in self.keywords):
            for k in self.keywords:
                if k not in keywords_list:
                    SyntaxError(f'Keyword {k} was not understood. Please check your syntax.')

        if self.keywords_simple:
            embedder.log('--> Parsed keywords are:\n    ' + ' '.join(self.keywords_simple) + '\n')

    def refine(self, options, *args):
        if len(self.embedder.objects) > 1:
            raise SystemExit(('REFINE keyword can only be used with one multimolecular file per run, '
                             f'in .xyz format. ({len(self.embedder.objects)} files found in input)'))

        options.noembed = True

    def _refine_operator_routine(self):
        if len(self.embedder.objects) > 1:
            raise SystemExit(('The refine> operator can only be used with one multimolecular file per run, '
                             f'in .xyz format. ({len(self.embedder.objects)} files found in input)'))

        from tscode.embeds import _get_monomolecular_reactive_indexes
        from tscode.graph_manipulations import get_sum_graph
        from tscode.utils import graphize

        # if there is a checkpoint with the same name, restart the run
        if f'TSCoDe_checkpoint_{self.embedder.stamp}.xyz' in os.listdir():
            self.embedder.objects[0].atomcoords = read_xyz(f'TSCoDe_checkpoint_{self.embedder.stamp}.xyz').atomcoords

            self.embedder.log(f'\n--> Read checkpoint from TSCoDe_checkpoint_{self.embedder.stamp}.xyz - resuming the run\n')

        self.embedder.structures = self.embedder.objects[0].atomcoords
        self.embedder.atomnos = self.embedder.objects[0].atomnos
        self.embedder.constrained_indexes = _get_monomolecular_reactive_indexes(self.embedder)
        self.embedder.ids = None
        self.embedder.energies = np.array([0 for _ in self.embedder.structures])
        self.embedder.exit_status = np.ones(self.embedder.structures.shape[0], dtype=bool)
        self.embedder.embed_graph = get_sum_graph([graphize(self.embedder.structures[0], self.embedder.atomnos)], self.embedder.constrained_indexes[0])

        if self.embedder.options.rmsd is None:
            # set this only if user did not already specify a value
            self.embedder.options.rmsd = 0.5 

        self.embedder.objects[0].compute_orbitals()

    def bypass(self, options, *args):
        options.bypass = True
        options.optimization = False

    def confs(self, options, *args):
        kw = self.keywords_simple[self.keywords.index('CONFS')]
        options.max_confs = int(kw.split('=')[1])

    def suprafac(self, options, *args):
        options.suprafac = True

    def deep(self, options, *args):
        options.options.rmsd = 0.3
        options.rotation_steps = 72
        options.max_clashes = 1
        options.clash_thresh = 1.4

    def rotrange(self, options, *args):
        kw = self.keywords_simple[self.keywords.index('ROTRANGE')]
        options.rotation_range = int(kw.split('=')[1])

    def steps(self, options, *args):
        kw = self.keywords_simple[self.keywords.index('STEPS')]
        options.custom_rotation_steps = int(kw.split('=')[1])

    def rmsd(self, options, *args):
        kw = self.keywords_simple[self.keywords.index('RMSD')]
        options.rmsd = float(kw.split('=')[1])

    def noopt(self, options, *args):
        options.optimization = False

    def ffopt(self, options, *args):
        kw = self.keywords_simple[self.keywords.index('FFOPT')]
        value = kw.split('=')[1].upper()
        if value not in ('ON', 'OFF'):
            raise SystemExit('FFOPT keyword can only have value \'ON\' or \'OFF\' (i.e. \'FFOPT=OFF\')')

        options.ff_opt = True if value == 'ON' else False

    def bypass(self, options, *args):
        options.bypass = True
        options.optimization = False

    def dist(self, options, *args):
        kw = self.keywords_simple[self.keywords.index('DIST')]
        orb_string = kw[5:-1].lower().replace(' ','')
        # orb_string looks like 'a=2.345,b=3.456,c=2.22'

        embedder = args[0]
        embedder._set_custom_orbs(orb_string)

    def clashes(self, options, *args):
        kw = self.keywords_simple[self.keywords.index('CLASHES')]
        clashes_string = kw[8:-1].lower().replace(' ','')
        # clashes_string now looks like 'num=3,dist=1.2'

        for piece in clashes_string.split(','):
            s = piece.split('=')
            if s[0].lower() == 'num':
                options.max_clashes = int(s[1])
            elif s[0].lower() == 'dist':
                options.clash_thresh = float(s[1])
            else:
                raise SyntaxError((f'Syntax error in CLASHES keyword -> CLASHES({clashes_string}).' +
                                    'Correct syntax looks like: CLASHES(num=3,dist=1.2)'))
        
    def newbonds(self, options, *args):
        kw = self.keywords_simple[self.keywords.index('NEWBONDS')]
        options.max_newbonds = int(kw.split('=')[1])

    def neb(self, options, *args):
        options.neb = Truthy_struct()
        options.neb.images = 6
        options.neb.preopt = False

        kw = self.keywords_simple[self.keywords.index('NEB')]
        neb_options_string = kw[4:-1].lower().replace(' ','')
        # neb_options_string now looks like 'images=8,preopt=true' or ''

        for piece in neb_options_string.split(','):
            s = piece.split('=')
            if s[0].lower() == 'images':
                options.neb.images = int(s[1])
            elif s[0].lower() == 'preopt':
                if s[1].lower() == 'true':
                    options.neb.preopt = True
            else:
                raise SyntaxError((f'Syntax error in NEB keyword -> NEB({neb_options_string}).' +
                                    'Correct syntax looks like: NEB(images=8,preopt=true)'))
        
        options.neb = Truthy_struct()
        options.neb.images = 6
        options.neb.preopt = False

        kw = self.keywords_simple[self.keywords.index('NEB')]
        neb_options_string = kw[4:-1].lower().replace(' ','')
        # neb_options_string now looks like 'images=8,preopt=true' or ''

        for piece in neb_options_string.split(','):
            s = piece.split('=')
            if s[0].lower() == 'images':
                options.neb.images = int(s[1])
            elif s[0].lower() == 'preopt':
                if s[1].lower() == 'true':
                    options.neb.preopt = True
            else:
                raise SyntaxError((f'Syntax error in NEB keyword -> NEB({neb_options_string}).' +
                                    'Correct syntax looks like: NEB(images=8,preopt=true)'))

    def level(self, options, *args):
        kw = self.keywords_simple[self.keywords.index('LEVEL')]
        options.theory_level = kw.split('=')[1].upper().replace('_', ' ')

        options.theory_level = options.theory_level.replace('[', '(').replace(']', ')')
        # quick fix for testing: allows the use of square brackets
        # in place of round, so that the LEVEL keyword is not
        # mistaken for one with sub-arguments. To be better addressed 
        # when/if a major rewrite of the option setting happens.

    def fflevel(self, options, *args):
        kw = self.keywords_simple[self.keywords.index('FFLEVEL')]
        options.ff_level = kw.split('=')[1].upper().replace('_', ' ')

    def rigid(self, options, *args):
        options.rigid = True

    def nci(self, options, *args):
        options.nci = True

    def onlyrefined(self, options, *args):
        options.only_refined = True

    def let(self, options, *args):
        options.let = True

    def check(self, options, *args):
        options.check_structures = True

    def kcal(self, options, *args):
        kw = self.keywords_simple[self.keywords.index('KCAL')]
        options.kcal_thresh = float(kw.split('=')[1])

    def shrink(self, options, *args):
        options.shrink = True
        kw = self.keywords_simple[self.keywords.index('SHRINK')]

        parsed = kw.split('=')
        options.shrink_multiplier = float(parsed[1]) if len(parsed) > 1 else 1.5

    def enantiomers(self, options, *args):
        options.keep_enantiomers = True

    def debug(self, options, *args):
        options.debug = True

    def procs(self, options, *args):
        kw = self.keywords_simple[self.keywords.index('PROCS')]
        options.procs = int(kw.split('=')[1])

    def threads(self, options, *args):
        kw = self.keywords_simple[self.keywords.index('THREADS')]
        options.threads = int(kw.split('=')[1])

    def ezprot(self, options, *args):
        options.double_bond_protection = True

    def calc(self, options, *args):
        kw = self.keywords_simple[self.keywords.index('CALC')]
        options.calculator = kw.split('=')[1]

    def ffcalc(self, options, *args):
        kw = self.keywords_simple[self.keywords.index('FFCALC')]
        options.ff_calc = kw.split('=')[1]

    def mtd(self, options, *args):
        if options.calculator != 'XTB':
            raise SystemExit(('Metadynamics augmentation can only be run with the XTB calculator.\n'
                                'Change it in settings.py or use the CALC=XTB keyword.\n'))
        options.metadynamics = True

    def saddle(self, options, *args):
        if not options.optimization:
            raise SystemExit('SADDLE keyword can only be used if optimization is turned on. (Not compatible with NOOPT).')
        options.saddle = True

    def ts(self, options, *args):
        if not options.optimization:
            raise SystemExit('TS keyword can only be used if optimization is turned on. (Not compatible with NOOPT).')

        self.embedder._setup(p=False)
        # early call of setup function to get the self.embedder.embed variable

        if '?' in self.embedder.pairings_table or (
            self.embedder.embed in ('cyclical','chelotropic') and len(self.embedder.pairings_table) < len(self.embedder.objects)) or (
            self.embedder.embed == 'string' and not self.embedder.pairings_table):

            raise SystemExit('TS keyword does not have sufficient pairing information to run. Make sure you specify the\n'
                             'label of each atomic pairing with the correct set of letters - "a", "b" or "c" for reactive atoms\n'
                             'and "x", "y" or "z" for non-covalent interactions holding the TS together.')

        if self.embedder.embed == 'dihedral':
            raise SystemExit('TS keyword not available with diheral embeds.\n'
                             'The embed itself yields first-order saddle point optimized structures.')

        options.ts = True

    def solvent(self, options, *args):
        kw = self.keywords_simple[self.keywords.index('SOLVENT')]
        options.solvent = kw.split('=')[1].lower()

    def pka(self, options, *args):
        kw = self.keywords_simple_case_sensitive[self.keywords.index('PKA')]
        pka_string, pka = kw.split('=')
        molname = pka_string[4:-1].replace(' ','')

        if molname in [mol.name for mol in self.embedder.objects]:
            if any([f'pka>{molname}' in op.replace(' ', '') for op in self.embedder.options.operators]):
                self.embedder.pka_ref = (molname, float(pka))
                return

        raise SyntaxError(f'{molname} must be present in the molecule lines, along with the pka> operator. Syntax: pka(mol.xyz)=n')

    def csearch(self, options, *args):
        options.csearch_aug = True

    def set_options(self):

        # self.keywords = sorted(self.keywords, key=lambda x: __keywords__.index(x))

        for kw in self.keywords:
            setter_function = getattr(self, kw.lower())
            setter_function(self.embedder.options, self.embedder, *self.args)

        if any('refine>' in op for op in self.embedder.options.operators) or self.embedder.options.noembed:
            self._refine_operator_routine()
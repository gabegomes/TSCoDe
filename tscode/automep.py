import time

import numpy as np
from networkx import cycle_basis

from tscode.algebra import dihedral
from tscode.calculators._xtb import xtb_opt
from tscode.graph_manipulations import neighbors
from tscode.optimization_methods import optimize
from tscode.utils import graphize, write_xyz


def automep(embedder, n_images=7):

    assert embedder.options.calculator == "XTB"

    mol = embedder.objects[0]
    coords = mol.atomcoords[0]

    # Get cycle indices bigger than 6
    graph = graphize(coords, mol.atomnos)
    cycles = [l for l in cycle_basis(graph) if len(l) == 7]
    assert len(cycles) == 1, "Automep only works for 7-membered ring flips at the moment"

    embedder.log('--> AutoMEP - Building MEP for 7-membered ring inversion')
    embedder.log(f'    Preoptimizing starting point at {embedder.options.calculator}/{embedder.options.theory_level}({embedder.options.solvent}) level')

    coords, _, _ = optimize(
                            coords,
                            mol.atomnos,
                            embedder.options.calculator,
                            method=embedder.options.theory_level,
                            procs=embedder.procs,
                            solvent=embedder.options.solvent,
                            title=f'temp',
                            logfunction=embedder.log,
                            )

    dihedrals = cycle_to_dihedrals(cycles[0])
    exocyclic = get_exocyclic_dihedrals(graph, cycles[0])

    start_angles = np.array([dihedral(coords[d]) for d in dihedrals+exocyclic])
    target_angles = np.array([0 for _ in dihedrals] + [180 for _ in exocyclic])
    multipliers = np.linspace(1, -1, n_images)

    mep_angles = [(start_angles * m + target_angles * (1-m)) % 360 for m in multipliers]

    mep = []
    for i, m_a in enumerate(mep_angles):
        t_start = time.perf_counter()
        coords, _, _ = xtb_opt(coords,
                                mol.atomnos,
                                constrained_dihedrals=dihedrals+exocyclic,
                                constrained_dih_angles=m_a,
                                method=embedder.options.theory_level,
                                solvent=embedder.options.solvent,
                                procs=embedder.procs)
        embedder.log(f'    - optimized image {i+1}/{len(mep_angles)} ({round(time.perf_counter()-t_start, 3)} s)')
        mep.append(coords)

    with open(f"{mol.rootname}_automep.xyz", "w") as f:
        for c in mep:
            write_xyz(c, mol.atomnos, f)

    embedder.log(f"\n--> Saved autogenerated MEP as {mol.rootname}_automep.xyz\n")

    return f"{mol.rootname}_automep.xyz"

def get_exocyclic_dihedrals(graph, cycle):
    '''
    '''
    exo_dihs = []
    for index in cycle:
        for exo_id in neighbors(graph, index):
            if exo_id not in cycle:
                dummy1 = next(i for i in cycle if i not in (exo_id, index) and i in neighbors(graph, index))
                dummy2 = next(i for i in cycle if i not in (exo_id, index, dummy1) and i in neighbors(graph, dummy1))
                exo_dihs.append([exo_id, index, dummy1, dummy2])

    return exo_dihs    

def cycle_to_dihedrals(cycle):
    '''
    '''
    dihedrals = []
    for i in range(len(cycle)):

        a = cycle[i % len(cycle)]
        b = cycle[(i+1) % len(cycle)]
        c = cycle[(i+2) % len(cycle)]
        d = cycle[(i+3) % len(cycle)]
        dihedrals.append([a, b, c, d])
    return dihedrals
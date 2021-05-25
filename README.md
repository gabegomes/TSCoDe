# TSCoDe - Transition State Conformational Docker

  

<div align="center">

 [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

TSCoDe is the first systematical conformational embedder for bimolecular and trimolecular chemical reactions. It is able to generate a comprehensive set of both regioisomeric and stereoisomeric poses for molecular arrangements, provided the atoms that will be reacting. By feeding the program with conformational ensembles, it also generates all conformations combinations It supports both open and cyclical transition states, exploring all regiosomeric and stereoisomeric poses.

TSCoDe is written mostly in Python, with some libraries optionally boosted via Cython. It leverages the numpy library to do the linear algebra required to translate and rotate molecules, and the [ASE](https://github.com/rosswhitfield/ase) environment to perform a set of manipulation on the provided structures

## What the program can do (well)
## What the program can do (sometimes)
## What the program cannot do
## Usage

### Input formatting
The program is 
 
  
  
  
### Keywords
- **SUPRAFAC** - Only retain suprafacial orbital configurations in cyclical TSs. Thought for Diels-Alder reactions.


- **DEEP** - Performs a deeper search, retaining more starting points for calculations and smaller turning angles. Equivalent to `THRESH=0.3 STEPS=12 CLASHES=(num=5, dist=1)`


- **NOOPT** - Skip the optimization steps, directly writing structures to file.

  

- **STEPS** - Manually specify the number of steps to be taken in scanning rotations. The standard value of 6 will perform six 60° turns. Syntax: `SCAN=n`, where n is an integer. **UPDATE**

  

- **BYPASS** - Debug keyword. Used to skip all pruning steps and directly output all the embedded geometries.

  

- **THRESH** - RMSD threshold (Angstroms) for structure pruning. The smaller, the more retained structures. Default is 0.5 A. Syntax: `THRESH=n`, where n is a number.

  

- **DIST** - Manually imposed distance between specified atom pairs, in Angstroms. Syntax uses parenthesis and commas: `DIST(a=2.345, b=3.67, c=2.1)`

  

- **CLASHES** - Manually specify the max number of clashes and the distance threshold at which two atoms are considered clashing. The more forgiving, the more structures will reach the geometry optimization step. Syntax: `CLASHES(num=3, dist=1.2)`

  

- **NEWBONDS** - Manually specify the maximum number of "new bonds" that a TS structure can have to be retained and not to be considered scrambled. Default is 1. Syntax: `NEWBONDS=1`

  

- **NEB** - Perform an automatical NEB TS search after the partial optimization step, inferring reagents and products. This option is only really usable for *associative* reactions, where two (or more) molecules are bound together (or strongly interacting) after the reaction, with no additional species involved. For example, cycloaddition reactions are great candidates while atom transfer reactions (*i.e.* epoxidations) are not.

  

- **LEVEL** - Manually set the MOPAC theory level to be used, default is PM7. Syntax: `LEVEL=PM7`

  

- **RIGID** - Avoid bending structures to better build TSs.

  

- **NONCI** - Avoid estimating and printing non-covalent interactions.

  

- **ONLYREFINED** - Discard structures that do not successfully refine bonding distances.

  

- **LET** - Overrides safety checks that prevent the program from running too large calculations.
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTczODc5MzAxNCwtNjcyMTE4NTYwXX0=
-->
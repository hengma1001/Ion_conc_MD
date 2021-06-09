import os
import pymol as pm
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    '-f', action='store', 
    default='AAAAAAAAA', help='Input peptide sequence.')
parser.add_argument(
    '-o', action='store', 
    default='out.pdb', help='Out PDB file.')
args = parser.parse_args()
print(args.f, args.o)
pm.editor.build_peptide(args.f)
pm.cmd.save(args.o, 'all')


gmx_command = 'editconf -f {0} -o {0} -c -box 6 6 30 '.format(args.o) 
print(gmx_command)
os.system(gmx_command)
gmx_command = 'echo \'1 \n 1\'|pdb2gmx -f {0} -o {0} -ignh'.format(args.o)
print(gmx_command)
os.system(gmx_command)

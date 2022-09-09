#!/usr/bin/python3

import sys, random, math
from pathlib import Path
from Bio import SeqIO

str_program = Path(__file__).name
print("This is honzo's {0} for selecting subsets of FASTA sequences".format(str_program))

bln_random = False
int_nseqs = 10

help_menu = \
"""
----------------------------------[ HELP MENU ]---------------------------------

    USAGE: 
    python {p} -f <filename>

    PARAMETERS:
    -h/--help       : shows this menu
    -f/--file       : <path> indicate input FASTA file
    -n/--nseqs      : [default={n}] indicate how many sequences to keep
    -r/--rand       : [default={r}] indicate whether to select sequences
                        randomly (True) or at equidistance intervals (False)

--------------------------------------------------------------------------------
""".format(p=str_program, n=int_nseqs, r=bln_random)


# retrieving user arguments
args = sys.argv
for i, arg in enumerate(args):
    if arg == ("-f" or "--file"):
        pth_input = Path(args[i+1])
    elif arg == ("-n" or "--nseqs"):
        int_nseqs = int(args[i+1])
    elif arg == ("-r" or "--rand"):
        bln_random = True
    elif arg == ("-h" or "--help"):
        print(help_menu)
        quit()
    elif arg[0] == "-":
        print("[WARNING] Unrecognized argument: {0}".format(arg))
    

with open(pth_input) as handle:
    lst_records = list(SeqIO.parse(handle, "fasta"))

int_nrecs = len(lst_records)
print("---> {0} sequences found in file: {1}".format(int_nrecs, pth_input))

if len(lst_records) <= int_nseqs:
    print("[ERROR] Not enough sequences in file for selection.")
    quit()

if bln_random:
    lst_subset = random.sample(lst_records, k=int_nseqs)
else:
    if int_nrecs//int_nseqs < 2:
        print("[WARNING] Not enough sequences for random selection")
    lst_subset = []
    for i in range(0, int_nrecs, math.ceil(int_nrecs/int_nseqs)):
        lst_subset.append(lst_records[i])

pth_output = pth_input.parent / (pth_input.stem + "_subset.fasta")
print("[sf] Chosen {0} of {1} accessions:".format(len(lst_subset), len(lst_records)))
[print(rec.id, end=", ") for rec in lst_subset]

print("\n[sf] Writing to file: {0}".format(pth_output))

with open(pth_output, "w") as handle:
    SeqIO.write(lst_subset, handle, "fasta")

print("[sf] Program complete.\n")


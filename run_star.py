#!/usr/bin/python3

import os, sys, shutil
from pathlib import Path


genome_dirs = {
    "sv18749": "--genomeDir /mnt/tank/bench/data/STAR_INDEX_SV18749TARGETS/",
    "hg38": "--genomeDir /mnt/tank/bench/data/STAR_INDEX_HG38_GENOME/"
}

for i, arg in enumerate(sys.argv):
    if arg == "-g":
        str_genome = sys.argv[i+1]
    elif arg == "-i":
        pth_input = Path(sys.argv[i+1])

    elif arg == ("-h" or "--help"):
        print("\nUSAGE: run_star.py -i <inputfile> -g <genome>")
        print("Available genomes:")
        for g in genome_dirs.keys(): print("-", g)
        print()
        quit()


genome = genome_dirs[str_genome]
os.chdir(pth_input.parent)
input = "--readFilesIn {0}".format(pth_input)

outdir = pth_input.stem+"_aligned"
try: 
    os.mkdir(outdir)
except: 
    shutil.rmtree(outdir)
    os.mkdir(outdir)

outname = "--outFileNamePrefix {1}/{0}".format(pth_input.stem + "_", outdir)

star = "/mnt/tank/bench/scripts/RNASeqBeta/bin/STAR-2.7.0e/bin/Linux_x86_64_static/STAR"
star = "STAR"
# defaults:  --outFilterMatchNmin 0 
modes = "--runThreadN 24 --runMode alignReads --outSAMtype BAM Unsorted --outSAMattributes All --readFilesCommand zcat --outSAMunmapped None --genomeLoad NoSharedMemory --alignEndsType Local --outReadsUnmapped Fastx"
params = "--outFilterScoreMinOverLread 0.3 --outFilterMatchNminOverLread 0.3 --outFilterMultimapNmax 1000000 --outFilterMismatchNoverLmax 0.3 --outFilterMismatchNmax 1 --alignIntronMax 1 --alignIntronMin 2"
#out1 = ">> ./RunStar.log"
#out2 = "2>> ./RunStar.err"

cmd = "{s} {m} {p} {g} {i} {o}".format(s=star, m=modes, p="params", g=genome, i=input, o=outname)
print("[cmd]", cmd)
os.system(cmd)

#!/home/sbsuser/miniconda3/bin/python

import sys
import gzip
from Bio import SeqIO
from pathlib import Path

umi_length = 6
for i, arg in enumerate(sys.argv):
    if arg == ("-f" or "--file"):
        pth_input = Path(sys.argv[i+1])
    elif arg == ("-l" or "--left"):
        umi_location = "left"
    elif arg == ("-r" or "--right"):
        umi_location = "right"
    elif arg == ("-n" or "--length"):
        umi_length = int(sys.argv[i+1])

print("Processing file: {0}".format(pth_input.name))
if ".fasta" in pth_input.suffixes:
    str_extension = "fasta"
elif ".fastq" in pth_input.suffixes:
    str_extension = "fastq"

if pth_input.suffix == ".gz":
    with gzip.open(pth_input, "rt") as handle:
        records = list(SeqIO.parse(handle, str_extension))
else:
    with open(pth_input, "rt") as handle:
        records = list(SeqIO.parse(handle, str_extension))

umi_counts = {}

for i, record in enumerate(records):
    if i % (len(records) // 10) == 0:
        print(".", end="", flush=True)

    if umi_location == "left":
        umi = record.seq[:umi_length]
    elif umi_location == "right":
        umi = record.seq[-umi_length:]

    if umi in umi_counts:
        umi_counts[umi] += 1
    else:
        umi_counts[umi] = 1

umi_sorted = {k: v for k, v in sorted(umi_counts.items(), key=lambda item: item[1], reverse=True)}

pth_output = pth_input.parent / (pth_input.name.split(".")[0]+"_umicounts.txt")
with open(pth_output, "wt") as wf_output:
    wf_output.write("UMI\tcount\n")
    for key in umi_sorted:
        wf_output.write("{0}\t{1}\n".format(key, umi_sorted[key]))

print("\tdone")

# honzo_tools
Generic tools used to handle/visualize bioinformatics data

## Generic tools
### revc
Python-based script to generate a reverse complement of a string. 
Supports ambiguous and degenerate bases.
USAGE: revc AGTCGATGCAGCAT

### mh
Python-based script meant to write center-aligned comments in a text file

### merger.py
merges FASTQ files from run1 and run2


## NGS-related tools
### coverage_calculator.py
Using a reference genome and a SAM/BAM file generated based on the reference, this script allows us to visualize the depth at each position of the chromosome. 
The script will also calculate the coverage on each chromosome and the average depth

BASIC USAGE: coverage_calculator.py -f <sam/bam file> -r <reference fasta>

### umiprofiling.py
Gets the first 'N' bases of all the reads in an unzipped fastq file to writes the number of occurrences of each combination

USAGE: umiprofiling.py <fastq file>

### find_mirnas.R
Created this script in response to a tech support question. This script finds genes that are common between multiple samples and generates a dataframe with the counts. The script is also capable of detecting the most variable genes.

# honzo_tools
Generic tools by honzo

## Generic scripts
### revc
Python-based script to generate a reverse complement of a string. 
Supports ambiguous and degenerate bases.
USAGE: revc AGTCGATGCAGCAT

### mh
Python-based script meant to write center-aligned comments in a text file
Flags are used to specify the character type (c) or indentation/tab level (t)
USAGE mh "This is a header"


## NGS-related scripts
### coverage_calculator.py
Using a reference genome and a SAM/BAM file generated based on the reference, this script allows us to visualize the depth at each position of the chromosome. 
The script will also calculate the coverage on each chromosome and the average depth

USAGE: coverage_calculator.py [options] -f <sam/bam file> -r <reference fasta>

### readlengths.py
Generates IQR and histograms showing the distribution of read lengths in an uncompressed FASTQ

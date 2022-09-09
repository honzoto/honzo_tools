#!/home/sbsuser/miniconda3/bin/python

import glob, os, sys, shutil
import subprocess
from pathlib import Path


version = "1.1"
script_name = Path(__file__).name

"""
HAHN'S NOTES


"""

# ======================================[ VARIABLE DECLARATION ]======================================

# Global variables
adapter_seq = "GATCGGAAGAGCACACGTCTGAACTCCAGTCAC"
umi_pattern = "NNNNNN"
tf_pairedend = False

star_params = ["STAR", "--runThreadN", "24", "--runMode", "alignReads", "--alignEndsType", "Local"]
star_params += ["--outSAMunmapped", "None", "--outReadsUnmapped", "Fastx", "--readFilesCommand", "zcat"]
star_params += ["--genomeLoad", "NoSharedMemory"]

star_genomedirs = {
    "sv18749": "/mnt/tank/bench/data/STAR_INDEX_SV18749/",
    "hg38": "/mnt/tank/bench/data/STAR_INDEX_HG38_GENOME/",
    "hg38rrna": "/mnt/tank/bench/data/STAR_INDEX_HG38_RRNA/"
}

# dependencies
EXE_CUTADAPT = "/home/sbsuser/miniconda3/bin/cutadapt"
EXE_PICARD = "/mnt/tank/bench/programs/picard/build/libs/picard.jar"
EXE_STAR = "/mnt/tank/bench/scripts/exceRpt/exceRpt_bin/STAR-2.7.0e/bin/Linux_x86_64_static/STAR"
EXE_UMITOOLS = "/home/sbsuser/miniconda3/bin/umi_tools"
EXE_FASTQC = "/home/linuxbrew/.linuxbrew/bin/fastqc"
EXE_MULTIQC = "/home/sbsuser/miniconda3/bin/multiqc"

help_menu = """
----------------------------------[ HELP MENU ]---------------------------------

    -h/--help       : shows this menu
    -p/--project    : <dir> name of the project folder
    -g/--genomes	: <str> reference genome to use*

*available STAR genomes: {g}

--------------------------------------------------------------------------------
""".format(g=star_genomedirs.keys())


# ----------------------------------------[ Input Validation ]----------------------------------------

for i, arg in enumerate(sys.argv):
	if arg == ("-p" or "--project"):
		PROJECT = sys.argv[i+1]
	elif arg == ("-g" or "--genome"):
		genome = sys.argv[i+1]
	elif arg == ("-a" or "--aligner"):
		aligner = sys.argv[i+1]
	elif arg == ("-h" or "--help"):
		print(help_menu); quit()


if len(sys.argv) < 2:
	print("Insufficient arguments entered. Use -h/--help option for help."); quit()

STAR_GENOME = ["--genomeDir", star_genomedirs[genome.lower()]]

# ======================================[ CLASSES AND FUNCTIONS ]=====================================

def get_nseqs(filename):
	cmd = "zcat {0} | echo $((`wc -l`/4))".format(filename)
	print("[cmd]", cmd)
	return int(subprocess.check_output(cmd, shell=True, text=True))

def run_cmd(cmd, write_stdout=True):
	str_cmd = " ".join(cmd)
	print("[cmd]", str_cmd)
	wf_samplelog.write("[cmd] {0}\n".format(str_cmd))

	if write_stdout:
		subprocess.run(cmd, stdout=wf_samplelog)
	else:
		subprocess.run(cmd)
	return

def align_star(params, query, genome: list):
	pth_query = Path(query)
	indir = ["--readFilesIn", query]
	outdir = ["--outFileNamePrefix", str(pth_query.parent/pth_query.stem)+"_"]
	cmd = params + genome + indir + outdir
	run_cmd(cmd)
	return

# ============================================[ WORKFLOW ]============================================

os.chdir("/mnt/tank/bench/projects/{0}".format(PROJECT))
FASTQS = sorted(glob.glob("*.fastq.gz"))

# Header
print("Initializing Honzo's {0} v{1} [dp] for PCR deduplication".format(script_name, version))
print("[dp] Project directory:", os.getcwd())
print("[dp] Reference genome:", STAR_GENOME[1])
print("[dp] FASTQS ({0}):".format(len(FASTQS)), FASTQS)

try: shutil.rmtree("DEDUPE_OUTPUT")
except: pass
os.mkdir("DEDUPE_OUTPUT")

statsummary = {} # [raw reads, adapter trimmed, ]
global wf_samplelog

for i, FASTQ in enumerate(FASTQS):
	print("\n[dp] Processing file-{1}: {0}".format(FASTQ, i+1))
	samplename = "_".join(Path(FASTQ).stem.split("_")[:3])
	LOGFILE = "DEDUPE_OUTPUT/log_{0}.txt".format(samplename)

	wf_samplelog = open(LOGFILE, "wt")
	statsummary[samplename] = []

	# get number of sequences in starting FASTQ
	n_reads = get_nseqs(FASTQ)
	statsummary[samplename].append(n_reads)
	print("---> [0] {0} raw reads found in FASTQ.".format(n_reads))

	# -------------------------------------[ Quality Control ]----------------------------------------
	print("[dp] Running FastQC on raw reads")
	cmd = [EXE_FASTQC, "*.fastq.gz"]
	run_cmd(cmd, write_stdout=False)

	print("[dp] Compiling FastQC outputs with MultiQC")
	cmd = [EXE_MULTIQC, "*"]
	run_cmd(cmd)
	
	# ------------------------------------[ Adapter Trimming ]----------------------------------------
	print("[dp] Trimming adapters")
	FASTQ_TRIMMED = "DEDUPE_OUTPUT/{0}_trimmed.fastq.gz".format(samplename)
	cmd = ["cutadapt", "-a", adapter_seq, "-o", FASTQ_TRIMMED, "--discard-untrimmed", FASTQ, "-m", "32"]
	print("[cmd]", " ".join(cmd))
	run_cmd(cmd, wf_samplelog)

	n_reads = get_nseqs(FASTQ_TRIMMED)
	statsummary[samplename].append(n_reads)
	print("---> [1] {0} adapter trimmed reads found.".format(n_reads))


	# -------------------------------------[ Processing UMIs ]----------------------------------------
	print("[dp] Processing UMIs with UMI-tools")

	FASTQ_UMIEXTRACTED = "DEDUPE_OUTPUT/{0}_trimmed_umiextracted.fastq.gz".format(samplename)
	# umi_tools extract --stdin=example.fastq.gz --bc-pattern=NNNNNNNNN --log=processed.log --stdout processed.fastq.gz
	cmd = [EXE_UMITOOLS, "extract", "--stdin="+FASTQ_TRIMMED, "--bc-pattern="+umi_pattern, "--log="+LOGFILE, "--stdout", FASTQ_UMIEXTRACTED]
	run_cmd(cmd, wf_samplelog)

	n_reads = get_nseqs(FASTQ_UMIEXTRACTED)
	statsummary[samplename].append(n_reads) 
	print("---> [2] {0} UMIs extracted from reads.".format(n_reads))

	# ------------------------------------[ Mapping to genome ]---------------------------------------
	print("[dp] Mapping to reference genome")
	align_star(star_params, query=FASTQ_UMIEXTRACTED, genome=STAR_GENOME)

	subprocess.run(cmd)


	wf_samplelog.close()

	print("breaking..."); break

	
print(statsummary)



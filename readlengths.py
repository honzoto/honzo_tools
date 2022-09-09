#!/usr/bin/python3

import glob, os
import statistics as stats
import numpy as np # for quartiles
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# experimenting with progress bar
#from alive_progress import alive_bar
import sys
import time
import threading

int_maxlen = 50 # upper limit of the histogram
str_project = "progressbar_test"
str_help = """
----------------------------------[ HELP MENU ]---------------------------------

USAGE   : readlengths.py -p <project> -l <max readlength>

-p      : <str> name of project relative to projects directory
-l      : <int> maximum readlength (used to set upper limit of histogram)


"""

for i in range(len(sys.argv)):
    if sys.argv[i] == "-p":
        str_project = sys.argv[i+1]
    elif sys.argv[i] == "-l":
        int_maxlen = int(sys.argv[i+1])
    elif sys.argv[i] == "-h" or sys.argv[i] == "--help":
        print(str_help)

os.chdir("/mnt/tank/bench/projects/{0}".format(str_project))

plt.rcParams["font.family"] = "Montserrat"
plt.rcParams['axes.axisbelow'] = True

# ======================================[ CLASSES AND FUNCTIONS ]=====================================

def update_progress(progress, barLength=40):
    # https://stackoverflow.com/questions/3160699/python-progress-bar
    # this function does not require any previously installed libraries

    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "\r\n"
    if progress >= 1:
        progress = 1
        status = "\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), round(progress*100), status)

    sys.stdout.write(text)
    sys.stdout.flush()

class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1: 
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False


# --- PROGRAM STARTS HERE ---

# remove all existing png files in the directory
#[os.remove(png) for png in glob.glob("*.png")]

lst_fastqs = sorted(glob.glob("*.fastq"))

print("Welcome to Hahn's {0} in {1}".format(__file__, os.getcwd()))
wf_out = open("stats_readlengths.csv", "w")
wf_out.write("filename,num_seqs,min,median,max,mean,stdev\n")

def read_fastq(filename):
    int_lines = sum(1 for line in open(filename))
    int_binsize = round(int_lines/100)

    with open(filename, "rt") as rf_fastq:
        lst_lens = []
        i = 0
        for line in rf_fastq:
            i += 1
            if not i%4 == 2:
                continue
            lst_lens.append(len(line.strip()))
            
            if i%int_binsize == 0:
                update_progress(i/int_lines)
        update_progress(i/int_lines)

    return lst_lens

f = 0 # for counting purposes
with PdfPages("plots_readlengths.pdf") as pdf:
    for fastq in lst_fastqs:
        f += 1
        str_name = fastq.split(".")[0]
        print("Working on file {0} of {1}: ".format(f, len(lst_fastqs))+fastq)

        lst_lens = read_fastq(fastq)
        str_progress = "Found {0} sequences. Processing statistics...".format(len(lst_lens))
        print(str_progress, end=" ")
        with Spinner():
            # get statistics
            int_min = min(lst_lens)
            int_max = max(lst_lens)
            flt_q1 = np.quantile(lst_lens, 0.25)
            flt_q2 = np.quantile(lst_lens, 0.50)
            flt_q3 = np.quantile(lst_lens, 0.75)
            flt_mean = stats.mean(lst_lens)
            flt_stdev = stats.stdev(lst_lens)
        
            line = [fastq, len(lst_lens), int_min, flt_q2, int_max, flt_mean, flt_stdev]
            wline = [str(l) for l in line]
            wf_out.write(",".join(wline)+"\n")

            print(" [done]")

        str_progress = "[Q1={0}, Q2={1}, Q3={2}] Plotting histogram...".format(flt_q1, flt_q2, flt_q3)
        print(str_progress, end=" ")
        with Spinner():
            fig, ax = plt.subplots(figsize=(11.0, 8.5))

            # styling: "#407BFF","#FF6066" <-- medium blue, red
            ax.grid(which='major', color='#E2E2E2', linestyle='--')
            ax.set_facecolor('#F5F5F5')
            for side in ["top","right"]:
                ax.spines[side].set_visible(False)

            ax.hist(lst_lens, bins=20, range=(0, int_maxlen), rwidth=0.9, color="#407BFF", zorder=1)
            ax.axvline(x=flt_q2, color="#FF6066")
            ax.axvspan(flt_q1, flt_q3, color="#F9E8E9", alpha=0.95, zorder=0)
            fig.suptitle(str_name, fontsize=18, fontweight='bold')
            ax.set_title("Q1 = {0}; Median = {1}; Q3 = {2}".format(flt_q1, flt_q2, flt_q3), fontsize=15)
            ax.set_ylabel("Number of reads", fontsize=14)
            ax.set_xlabel("Read Length (nt)", fontsize=14)

            #print("hz67 np median: {0}, stats median: {1}".format(flt_q2, stats.median(lst_lens)))
            pdf.savefig()
            plt.close()
            print(" [done]")

wf_out.close()
print("program complete.")

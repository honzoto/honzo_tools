import os, glob

print("... starting merger.py ...")
"""
This script takes two FASTQ files by the same name (one saved in Run1 folder, one in Run2)
and concatenates them. The merged file will be in a folder called "merged"

INSTRUCTIONS
1. paste this script in the same directory where you have the folders Run1 and RUn2
2. run the script
"""

lst_run1files = sorted(glob.glob("Run1/*.fastq.gz"))
lst_run2files = sorted(glob.glob("Run2/*.fastq.gz"))
print(len(lst_run1files), len(lst_run2files))

# for the future, check if this directory is already made
try: os.mkdir("merged")
except: print("merged folder already exists.")

if len(lst_run1files) == len(lst_run2files):
    for i in range(len(lst_run1files)):
        str_run1 = lst_run1files[i]
        str_run2 = lst_run2files[i]
        if str_run1.split("/")[-1] == str_run2.split("/")[-1]:
            str_merged = str_run1.replace("Run1/", "merged/")
            str_command = "cat {0} {1} > {2}".format(str_run1, str_run2, str_merged)
            print("[cmd]", str_command)
            os.system(str_command)
            
        else:
            print(str_run1+" and "+str_run2+" do not match.")

os.chdir("merged")
os.system("fastqc *.fastq.gz")
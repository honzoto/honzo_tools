import glob, os, re

datasets = sorted(glob.glob("ncbi_dataset*"))

labels = {
    0: "Metamycoplasma hominis",
    1: "Neisseria gonorrhoeae",
    2: "Neisseria meningitidis",
    3: "Pasteurella multocida",
    4: "Pediococcus acidilactici",
    5: "Peptostreptococcus anaerobius",
    6: "Cutibacterium acnes",
    7: "Proteus mirabilis",
    8: "Proteus vulgaris",
    9: "Providencia stuartii",
    10: "Pseudomonas aeruginosa",
    11: "Salmonella enterica subsp enterica serovar Minnesota",
    12: "Serratia marcescens",
    13: "Staphylococcus epidermidis",
    14: "Staphylococcus saprophyticus",
    15: "Streptococcus agalactiae",
    16: "Streptococcus anginosus",
    17: "Streptococcus pyogenes",
    18: "Streptococcus sanguinis",
    19: "Simian immunodeficiency virus",
    20: "Treponema Pallidum",
    21: "Ureaplasma urealyticum",
    22: "Veillonella parvula",
    23: "Vibrio parahaemolyticus",
    24: "Weissella paramesenteroides",
    25: "Yersinia enterocolitica"
}


for folder in datasets:
    idx = int(re.search("ncbi_dataset\((\d+)\)", folder).group(1))
    os.chdir(folder)
    os.system("mv ncbi_dataset/data/*/*.fna .")
    os.system("cat *.fna > ../{0}.fasta".format(labels[idx].replace(" ","_")))
    os.chdir("..")
message("Starting find_mirnas.R version 1.0")

# The purpose of this program is to find housekeeping miRNAs across biofluids

tf_manual <- FALSE

#'------------------------------[ SETTING UP ARGUMENTS AND DIRECTORIES ]------------------------------'

library(optparse) # to parse user arguments
library(dplyr)
library(edgeR) # to calculate cpm

# retrieving user arguments
option_list = list(
  make_option(c("-p", "--project"), type="character", default=NULL,
              help="Project archive name", metavar="character"),
  make_option(c("-b", "--biotype"), type="character", default=NULL,
              help="Biotype (plasma, serum, urine)", metavar="character"),
  make_option(c("-c", "--cutoff"), type="integer", default=0,
              help="[default=0] minimum count to be considered")
)

opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)
message("[fm17] finished reading user arguments")

if (tf_manual){
  message("[fm21] running script in manual mode.")
  opt$project <- "dev_mirna"
  opt$biotype <- "lung"
}

# setting up project directory and input files
dir_work = file.path("/mnt/tank/bench/projects/", opt$project)
setwd(dir_work)
str_outfile <- paste(opt$biotype, "_cv.txt", sep="")
lst_files <- Sys.glob(paste('*',opt$biotype,'.txt', sep=""))
message("This is find_mirnas.R for finding housekeeping miRNAs")
message(paste("Working in directory:", dir_work))
message(paste("Files found:", paste(lst_files, collapse=", ")))

#'--------------------------------------[ GETTING COMMON MIRNAS ]-------------------------------------'

lst_cpms <- list() # this list will hold all the count dataframes
# reading miRNA counts from tables in the directory
for (i in 1:length(lst_files)){
  str_file <- lst_files[i]
  message(paste("[fm44] reading file:", str_file))
  df_counts <- read.table(str_file, header=TRUE, sep="\t", row.names=1)
  
  # apply filtering based on minimum count
  row_sub <- apply(df_counts, 1, function(row) all(row >= opt$cutoff))
  df_counts_filtered <- df_counts[row_sub, ]
  df_cpms <- data.frame(cpm(df_counts_filtered))
  
  # Calculate CV for each of the miRNAs
  df_cpms$mean <- apply(df_cpms, 1, mean)
  df_cpms$sd <- apply(df_cpms, 1, sd)
  df_cpms[str_file] <- df_cpms$sd / df_cpms$mean
  
  #write.table(df_cpms, paste("cv_",str_file,sep=""), sep="\t")
  # subset by common rows between current dataframe and previous
  lst_cpms[[i]] <- df_cpms
  if (i == 1){
    lst_common <- row.names(df_cpms)
  } else {
    lst_common <- intersect(lst_common, row.names(df_cpms))
  }
  message(paste("[fm64] common miRNAs remaining:", length(lst_common)))
}

# isolate for CVs in a new dataframe
#df_cvs <- data.frame(row.names=lst_common)
df_cvs <- data.frame(row.names = sort(lst_common))
for (i in 1:length(lst_files)){
  df_current <- subset(lst_cpms[[i]], rownames(lst_cpms[[i]]) %in% lst_common)
  df_current_cv <- df_current[lst_files[i]]
  df_cvs[lst_files[i]] <- df_current_cv[order(row.names(df_current_cv)),]
}

#'------------------------------------[ ANALYZING CVs BY PROJECT ]------------------------------------'

# output the dataframe of CVs into a new file
df_cvs$mean_cv <- apply(df_cvs, 1, mean)
df_cvs$sd_cv <- apply(df_cvs, 1, sd)
df_cvs <- (df_cvs[order(df_cvs$mean_cv),])
write.table(df_cvs, str_outfile, quote=FALSE, col.names=NA, sep="\t")

# UPDATE NOTES
# version 1
# - created program to glob *_biotype.txt files in a project directory
# - the output is a dataframe of CVs, sorted from lowest to highest
# - added option 

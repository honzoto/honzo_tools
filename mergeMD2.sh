#!/bin/bash

while [[ $# -gt 0 ]]
do
key="$1"
case $key in
    -d|--directory)
    MIRDEEP_DIR="$2"
    shift # past argument
    shift # past value
    ;;
    -h|--help)
    HELP=true
    shift # past argument
    shift # past value
    ;;
    --verbose)
    VERBOSE=true
    shift # past argument
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

if [[ "$VERBOSE" = true ]]; then
	echo MIRDEEP_DIRECTORY  	= "${MIRDEEP_DIR}"
	echo ""
fi

if [[ -n $1 ]]; then
    echo "ERROR: No options have been chosen."
    echo "Please use mergeMD2.sh -h for usage and options."
    exit 0
fi

if [[ "$HELP" = true ]]; then
	echo "USAGE: mergeMD2.sh [-h] [-d]"
	echo ""
	echo "OPTIONAL PARAMETERS:"
	echo -e "  -h, --help\t\tShows this message"
	echo -e "  -d, --directory\t\tThe directory containing the mirDeep2 output files"
	exit 0
fi

if [ ! -d ${MIRDEEP_DIR} ]; then
	echo "This directory '${MIRDEEP_DIR}' does not exist."
else
	for DIR in `ls -d ${MIRDEEP_DIR}/*/`; do
		RESULTS=$(find ${DIR} -maxdepth 1 -name 'result*.csv')
		#tempSigToNoise=100 		
		tempAbsSigToNoise=100	#Temporarily sets a high number
		tempNegSigToNoise=-100
		echo ""
		echo $(basename "${DIR}") 
		echo "-----"
		echo ${RESULTS}
		while IFS= read -r line; do
			#echo "Reading"
			sigToNoise=$(echo "${line}" | cut -f8) 		#Looks for the Signal-To-Noise Column
			mdScore=$(echo "${line}" | cut -f1)			#Looks for the miRDeep2 Score Column

			#echo ${sigToNoise}

			#New Algorithm
			absSigToNoise=$(echo "${sigToNoise}-10" | bc -l | tr -d -)
			#echo "${sigToNoise}-10" | bc -l
			#echo ${absSigToNoise}

			if (( $(echo "${absSigToNoise} <= ${tempAbsSigToNoise}" | bc -l ) )); then
				tempAbsSigToNoise=${absSigToNoise}
				tempSigToNoise=${sigToNoise}
				mdScoreValue=${mdScore}
			fi
			sigToNoiseValue=${tempSigToNoise}

			# if (( $(echo "${sigToNoise}-10 >= 0" | bc -l) )); then
			# 	if (( $(echo "${sigToNoise}-10 <= ${tempSigToNoise}-10" | bc -l) )); then
			# 	#We use the (( numeric operator )) here since we are comparing numbers
			# 	#However, in this case, since we are using floats instead of integers, bash doesn't do the arithmetic operations
			# 	# the same way, so we have to pipe it to bc in order to determine if the statement was true or not				
			# 		tempSigToNoise=${sigToNoise}
			# 		mdScoreValue=${mdScore}
			# 	else
			# 		echo "ERROR POSITIVE: ${line}"
			# 	fi
			# elif (( $(echo "${sigToNoise}-10 < 0" | bc -l) )); then
			# 	if (( $(echo "-1*(${sigToNoise}-10) <= ${tempNegSigToNoise}-10" | bc -l) )); then
			# 		tempNegSigToNoise=${sigToNoise}
			# 		mdScoreNegValue=${mdScore}
			# 	else
			# 		echo "ERROR NEGATIVE: ${line}"
			# 	fi
			# else
			# 	echo "ERROR HOW...: ${line}"
			# fi
			# sigToNoiseValue=${tempSigToNoise}
		done <<< $(tail -n +2 ${RESULTS} | head -21)
		#To prevent the while loop from executing in a subshell, we feed in 23 lines from the actual file
		if [[ ${sigToNoiseValue} == 100 ]]; then
			echo ${DIR}
			sigToNoiseValue=${tempNegSigToNoise}
			mdScoreValue=${mdScoreNegValue}
		fi
		echo "Signal-To-Noise: ${sigToNoiseValue}" 		#This would be the actual Signal-To-Noise value we are going to use
		echo "miRDeep2 Score: ${mdScoreValue}"			#And this is the corresponding miRDeepScore Value that we will compare to

		#Afterwards we need to then get all of the novel miRNAs detected by mirDeep2

		#Find the Line Number where the Novel miRNAs end
		lineNumber=$(grep -n "mature miRBase miRNAs" ${RESULTS} | cut -d ":" -f1)
		lineNumber=$((lineNumber-30)) 		#This is -30 because the first 27 lines are the score and title "novel miRNAs"
											#afterwards, the 3 lines will be the space between the mature miRBase
											# and the end of the novel miRNAs
		count=0
		novelmiRNA=""
		while IFS= read -r line; do
			#The first line is still the title, so it will produce an error. Other than that no issue
			miRDeepScore=$(echo "${line}" | cut -f2)
			if (( $(echo "${miRDeepScore} >= ${mdScoreValue}" | bc -l) )); then
				novelmiRNA="${novelmiRNA}"$'\n'"${line}"
				(( count++ ))
			fi 
		done <<< $(tail -n +28 ${RESULTS} | head -${lineNumber})
		echo "Novel miRNAs: ${count}"
		echo ""
		echo $(grep "provisional id" ${RESULTS})
		echo "${novelmiRNA}"
	done
fi

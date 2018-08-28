#!/bin/bash


# This file should take input in the form of a file containing several lines 
# provided by the --file flag.

# Below is preprepared code to accept the command line arguments we will be providding to this file. The rest is up to you. 

# Change directory to where the script is stored, not where it is run from
scriptPath=$(cd -P -- "$(dirname -- "$0")" && pwd -P)
cd $scriptPath
source participantConfig.sh
# This brought in the following variables 
# $chainName
# $rpcuser
# $rpcpassword
# $rpcport

die() {
    printf '%s\n' "$1" >&2
    exit 1
}

show_help() {
cat << EOF
Usage: ${0##*/} [--file arg]...
    -h                              Display this help and exit
    --file <arg> | --file=<arg>     Insert all lines in the provided file. 
EOF
}

# Initialize all the option variables.
# This ensures we are not contaminated by variables from the environment.
file=

# Process arguments and set variables. 
case $1 in
    -h|-\?|--help)
        show_help    # Display a usage synopsis.
        exit
        ;;
    --file)       # Takes an option argument; ensure it has been specified.
        if [ "$2" ]; then
            file=$2
            shift
        else
            die 'ERROR: "--file" requires a non-empty option argument.'
        fi
        ;;
    --file=?*)
        file=${1#*=} # Delete everything up to "=" and assign the remainder.
        ;;
    --file=)         # Handle the case of an empty --file=
        die 'ERROR: "--file" requires a non-empty option argument.'
        ;;
    -?*)
        printf 'WARN: Unknown option (ignored): %s\n' "$1" >&2
        ;;
    *)  die 'ERROR: No input provided. Please run with --file'
        break
esac


# =====================================================
# Place your code below this comment block
# 
# The following variables have been set for you. 
# $chainName        The name of the chain
# $rpcuser          The rpc username for the chain
# $rpcpassword      The rpc password for the chain    
# $rpcport          The rpc port for the chain
# $file             The path to a file containting several lines
# 
# 
# example code
# java -jar myInsert.jar $chainName $rpcuser $rpcport $rpcpassword file=$file
# 
# =====================================================

cd $scriptPath
python3 insert.py $file

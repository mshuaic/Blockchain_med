#!/bin/bash

# Testing for the following queries

# QUERY 1: user = 7 AND timestamp FROM 1522257730000 TO 1522449160000

# QUERY 2: resource = MOD_WormBase

# QUERY 3: user = 1 AND resource = TOPMed

# QUERY 4: node = 3 AND ref-id = 40345 SORTED_BY timestamp ASC

# Change directory to where the script is stored, not where it is run from
scriptPath=$(cd -P -- "$(dirname -- "$0")" && pwd -P)
cd $scriptPath

mkdir -p testResults

# Test query 1
time bash query.sh --user 7 --start_time 1522257730000 --end_time 1522449160000 > testResults/query1.txt
diff <(sort testResults/query1.txt) <(sort sampleResults/user_7_startTime_1522257730000_endTime_1522449160000.txt) | diffstat

# Test query 2
time bash query.sh --resource MOD_WormBase > testResults/query2.txt
diff <(sort testResults/query2.txt) <(sort sampleResults/resource_MOD_WormBase.txt) | diffstat

# Test query 3
time bash query.sh --user 1 --resource TOPMed > testResults/query3.txt
diff <(sort testResults/query3.txt) <(sort sampleResults/user_1_resource_TOPMed.txt) | diffstat

# Test query 4
time bash query.sh --node 3 --ref_id 40345 --sort_by timestamp --order asc > testResults/query4.txt
diff testResults/query4.txt sampleResults/node_3_ref-id_40345_sortby_timestamp.txt | diffstat
#!/usr/bin/env python

### IAPS Task Results Analysis Script
### Creator: Robert Kim
### Last Modifier: Robert Kim
### Version Date: 15 Jan 2017
### Python 2.7 

### Assumptions: 	IAPS_REFERENCE.csv is present and constant
### 				header fieldnames are constant across input files

import csv
import os
import sys
import time

### opens sys.stdout in unbuffered mode
### print (sys.stdout.write()) operation is automatically flushed after each instance
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

### set home directory
home_dir = os.path.dirname(os.path.abspath(__file__))
# home_dir = '/Volumes/projects_herting/NEAT/Visit_2/V2_Data'
os.chdir(home_dir)

### this function cures cancer
def analysis(in_file):
	with open(in_file, 'rb') as csvfile:
		reader = csv.DictReader(csvfile)
		header = reader.fieldnames
		raw_data = list(reader)

	### removes practice trials from data analysis and sorting
	raw_data[:] = [row for row in raw_data if row['trials.thisRepN']]

	ref_fields = ['valence_rank', 'valence_range', 'valence_mean', 'arousal_mean']
	new_fields = ['ref_' + s for s in ref_fields]
	header[1:1] = new_fields

	var = ['Valence_key.keys', 'Valence_key.rt', 'Arousal_key.keys', 'Arousal_key.rt']
	rank_cases = ['high', 'medium', 'low']
	range_cases = ['7to9', '4to6', '1to3']
	
	for row in raw_data:
		n = ref_img_list.index(row['stimFile'][ :row['stimFile'].index('.jpg')])
		row.update({x : reference[n][y] for x, y in zip(new_fields, ref_fields)})

		row[var[0]] = str_conv(row[var[0]], int)
		row[var[1]] = str_conv(row[var[1]], float)
		row[var[2]] = str_conv(row[var[2]], key_dict)
		row[var[3]] = str_conv(row[var[3]], float)

	raw_data[:] = sorted(raw_data, key=lambda row: row['ref_valence_mean'], reverse = True)

	rank_calc = [[avg_col(raw_data, col, 'ref_valence_rank', row) for col in var] for row in rank_cases]
	range_calc = [[avg_col(raw_data, col, 'ref_valence_range', row) for col in var] for row in range_cases]
	calc_header = ['valence_block', 'avg_valence_rating', 'avg_valence_rt', 'avg_arousal_rating', 'avg_arousal_rt']
	calc_results = 	[['all'] + [avg_col(raw_data, col, 'ref_valence_rank', *rank_cases) for col in var]] \
					+ [[x] + y for x, y in zip(rank_cases, rank_calc)] \
					+ [[x] + y for x, y in zip(range_cases, range_calc)]

	for row in calc_results:
		print "\t%s Valence Block Statistics: " % row[0].upper()
		print "\t\tAverage Valence Rating = %.3f" % row[1]
		print "\t\tAverage Valence Response Time = %.3fs" % row[2]
		print "\t\tAverage Arousal Rating = %.3f" % row[3]
		print "\t\tAverage Arousal Response Time = %.3fs" % row[4]

	basename = os.path.basename(in_file)
	n = basename.index('.csv')
	out_dir = "IAPS_analysis_results"
	calc_out_file = os.path.join(out_dir, basename[ :n] + "_ANALYSIS.csv")
	data_out_file = os.path.join(out_dir, basename[ :n] + "_SORTED.csv")
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)

	with open(calc_out_file, 'wb') as out_csv:
		writer = csv.writer(out_csv, delimiter = ',', quotechar = '"')
		writer.writerow(calc_header)
		writer.writerows(calc_results)

	with open(data_out_file, 'wb') as out_csv:
		writer = csv.DictWriter(out_csv, header, delimiter = ',', quotechar = '"')
		writer.writeheader()
		writer.writerows(raw_data)

def avg_col(arr, var, match, *case):	 
	temp = [row[var] for row in arr if row[match] in list(case) and row[var] not in ['None', '', None]]
	return float(sum(temp))/float(len(temp))

def key_dict(s):
	return 	{	'a' : 1,
				's' : 2,
				'd' : 3,
				'f' : 4,
				'g' : 5,
				'h' : 6,
				'j' : 7,
				'k' : 8,
				'l' : 9 	}.get(s.lower(), '')

def run_analysis(arr):
	error_files = []
	for x in arr:
		try:
			print "\n::::: ANALYZING %s :::::" % x
			analysis(x)
		except ZeroDivisionError: 
			print ">> ERROR READING " + x
			print ">> ZERO DIVISION ERROR: CHECK FILE CONSTRUCTION"
			error_files.append(x)

	if error_files:
		print "\n>> TOTAL OF %d INVALID FILES" % len(error_files)
		print ">> LIST OF FILES THAT THREW EXCEPTION:\n>>",
		print '\n>>'.join(error_files)

def str_conv(x, func):
	try:
		return func(x)
	except ValueError:
		return x

### MAIN ###

reference_csv = "IAPS_REFERENCE.csv"

try:
	with open(reference_csv, 'rb') as csvfile:
		reference = list(csv.DictReader(csvfile))
except IOError:
	sys.exit(	"EXITING OPERATION\n" + 
				"IAPS_REFERENCE.csv was not found in working directory.\n" + 
				"Please place %s into the proper directory (same as script file) and try again." % reference_csv	)

ref_img_list = [row['stimFile'] for row in reference]

print "Script file directory: %s" % home_dir
print "Subdirectories found in script file directory:\n"

for x in list(enumerate(next(os.walk(home_dir))[1])):
	print "    ", 
	print x
print ""

dir_input = raw_input("Please enter the desired working subdirectory: ")

try:
	dir_index = int(dir_input)
except ValueError:
	sys.exit(	"EXITING OPERATION\n" + 
				"No subdirectory was properly selected"		)

sub_dir = next(os.walk(home_dir))[1][dir_index]
print "\nNew working directory: %s" % os.path.join(home_dir, sub_dir)

csv_list = []

for root, dirs, files in os.walk(sub_dir):
    for f in files:
        if f.endswith(".csv"):
             csv_list.append(os.path.join(root, f))

if not csv_list:
	sys.exit(	"EXITING OPERATION\n" + 
				"No CSV files were found in working directory.\n" + 
				"Please place the script file into the proper directory and try again."	)

print "\nCSV files found in working directory:\n"

for x in list(enumerate(csv_list)):
	print "    ", 
	print (x[0], "/".join(x[1].strip("/").split('/')[1:]))
print ""

csv_input = raw_input("Please enter the desired CSV file index (or multiple indices separated by spaces): ")

if not csv_input:
	sys.exit(	"EXITING OPERATION\n" + 
				"No CSV files were properly selected"	)

csv_index = csv_input.split()
csv_index = [int(a) for a in csv_index]

if not all(n in range(len(csv_list)) for n in csv_index):
	sys.exit(	"EXITING OPERATION\n" +
				"INVALID ENTRY OF FILE INDICES"	)

input_list = [csv_list[n] for n in csv_index]
run_analysis(input_list)

print "\nOPERATION COMPLETED " + time.strftime("%d %b %Y %H:%M:%S", time.localtime())
# -------------------------------------------------------------------------------
# Name:        PBSAMR_CreateInput
# Purpose:     Create Input for the numerical experiment of
#              Raviv, Bukchin, de Koster (2022)
#
# Author:      Tal Raviv talraviv@tau.ac.il
#
# Created:     11-April-2022
# Copyright:   (c) Tal Raviv 2022
# Licence:     Free to use but please contact me before
# -------------------------------------------------------------------------------

"""
Each set of instances is defined by the dimensions of the PBS unit Lx times Ly and the location(s) of the IO point(s).
Each location is referred to by its horizontal and vertical position, where the bottom left corner is (0,0), and the top
right corner is (Lx-1, Ly-1).

Each group of instances in a dataset differs by the number of escorts and AMRs.  Instances within the same group differ
by the initial location of the target load, escorts (empty positions), and AMRs.

Each instance in a group is characterized by an integer number (typically consecutive numbers) used as a random seed for
generating the abovementioned initial locations.

To create a dataset, run the program as follow:

python3 PBSAMR_CreateInput <name> <Lx> <Ly> <num_of_escorts_range> <num_of_amrs_range> <replications_range> <IO1x, IO1y, IO2x, IO2y,...>

<name> is just a string to identify the dataset (e.g., edge, corner, center)
<Lx> <Ly> are the dimensions of the units

<num_escort_range> defines the range of the number of escorts in the data set. E.g., 3-6 will create instances with
3,4,5, and 6 escorts, while 3-9-3 will create instances with 3,6 and 9 escorts.

 <num_of_amrs_range> defines the range of the number of AMRs in the dataset using the same range syntax

It is important to understand that the groups of instances are defined by the <num_escort_range> and <num_of_amrs_range>
parameters. E.g., if the values of these parameters are 2-6-2 and 3-6-3, respectively, the dataset will include six groups:
2 escorts and 3 AMRs
2 escorts and 6 AMRs
4 escorts and 3 AMRs
4 escorts and 6 AMRs
6 escorts and 3 AMRs
6 escorts and 6 AMRs

<replications_range> defines the number of instances in each group and the seed number used to generate the initial
locations. E.g., 1-20 will create 20 instances for each group (the same "random" values each time the program is run with
the same parameters). To create different 20 instances with the same characteristics, one can use a different range, e.g., "21-40."

The list of parameters is ended by a list of locations (at any length) of IO points coordinates, <IO1x, IO1y, IO2x, IO2y,...>.

For example, the command line:
python3 CreateInstances Center 7 7 4-8-2 5-11-3 1-20 3 0

creates the 20 instances of each of the nine groups of the first dataset used in Section 5.2 in the paper. A 7x7 unit
with one IO point at the center of the lower wall of the units. Each group is defined by combining one value of
the number of escorts and one value of the number of AMRs.

The program's output is a CSV file that completely specifies all the instances and one pickle file for each instance.

The names of the pickle files are "<name>_<Lx>x<Ly>_IO<#IOs>_<#escorts>_<#amrs>_<seed#>.p"

E.g., "center_7x7_IO1_4_5_1_3_0.p"


The instances used for performance evaluation in Section 5.2 were created by running this script as follows

python3 CreateInstances Center 7 7 4-8-2 5-11-3 1-20 3 0
python3 CreateInstances Center 9 9 6-14-4 8-16-4 1-20 4 0
python3 CreateInstances Center 16 10 13-24-6 16-32-8 1-20 4 0 11 0
python3 CreateInstances Center 20 5 8-16-4 10-20-5 1-20 0 0 1 0 2 0 3 0 4 0 5 0 6 0 7 0 8 0 9 0 10 0 11 0 12 0 13 0 14 0 15 0 16 0 17 0 18 0 19 0


The the single I/O instances used in Section 5.3 where generated as follows

python3 CreateInstances Center 12 10 6-12-3 8-16-4 1-20 5 0
python3 CreateInstances Center 15 8 6-12-3 8-16-4 1-20 5 0
python3 CreateInstances Center 20 6 6-12-3 8-16-4 1-20 5 0
python3 CreateInstances Center 24 5 6-12-3 8-16-4 1-20 5 0

The multi I/O instances of this section where created by

python3 CreateInstances Center 12 10 6-12-3 8-16-4 1-20 0 0 1 0 2 0 3 0 4 0 5 0 6 0 7 0 8 0 9 0 10 0 11 0
python3 CreateInstances Center 15 8 6-12-3 8-16-4 1-20 0 0 1 0 2 0 3 0 4 0 5 0 6 0 7 0 8 0 9 0 10 0 11 0 12 0 13 0 14 0 15
python3 CreateInstances Center 20 6 6-12-3 8-16-4 1-20 0 0 1 0 2 0 3 0 4 0 5 0 6 0 7 0 8 0 9 0 10 0 11 0 12 0 13 0 14 0 15 0 16 0 17 0 18 0 19 0
python3 CreateInstances Center 24 5 6-12-3 8-16-4 1-20 0 0 1 0 2 0 3 0 4 0 5 0 6 0 7 0 8 0 9 0 10 0 11 0 12 0 13 0 14 0 15 0 16 0 17 0 18 0 19 0 20 0 21 0 22 0 23 0

"""

import sys
import pickle
from PBSCom import tuple_opl, str2range
import itertools
import random

if __name__ == '__main__':
    if len(sys.argv) < 9:
        print("usage: python", sys.argv[0],
              "<name> <Lx> <Ly> <num_of_escorts_range> <num_of_amrs_range> <replications_range>  <IO1x, IO1y, IO2x, IO2y,...> ")
        exit(1)

    inst_name = sys.argv[1].strip()
    Lx, Ly = int(sys.argv[2]), int(sys.argv[3])
    escorts_range = str2range(sys.argv[4])
    amrs_range = str2range(sys.argv[5])
    reps_range = str2range(sys.argv[6])
    ez = [int(a) for a in sys.argv[7:]]
    O = []
    for i in range(len(ez) // 2):
        O.append((ez[i * 2], ez[i * 2 + 1]))

    Locations = sorted(set(itertools.product(range(Lx), range(Ly))))

    file_name_base = f"{inst_name}_{Lx}x{Ly}_IOs{len(O)}"

    try:
        f_csv = open(file_name_base + ".csv", "w")
    except:
        print(f"Panic: cannot {file_name_base}.csv, make sure that it is not open in Excel")
        exit(1)

    f_csv.write("Lx x Ly, #IOs, #escorts, #AMRs, Replication#, IOs, Target, Escorts, AMRs\n")

    for num_of_escorts in escorts_range:
        for num_of_amrs in amrs_range:
            if num_of_escorts + num_of_amrs > Lx * Ly:
                break  # Since the AMRs are loacted under load the number of AMRs and esscort cannot exceed the number of cells
            for seed in reps_range:
                random.seed(seed)
                I = random.sample(sorted(set(Locations) - set(O)), 1)[
                    0]  # select a target load location that is not an IO location  - CHECK THIS
                E = sorted(random.sample(sorted(set(Locations) - set([I])),
                                         num_of_escorts))  # select escort location that is not the target
                random.seed(
                    seed + 1000)  # Take a different stream for the AMR initial location but make it consistant with the replication number
                A = sorted(
                    random.sample(sorted(set(Locations) - set(E)), num_of_amrs))  # select AMR locations not in escorts
                f_csv.write(
                    f"{Lx}x{Ly}, {len(O)}, {num_of_escorts}, {num_of_amrs}, {seed}, {tuple_opl(O)},{tuple_opl([I])}ß,{tuple_opl(E)},{tuple_opl(A)}\n")
    f_csv.close()

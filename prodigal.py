"""
A script to call Prodigal to predict both genes and proteins.

Input:
File or folder with contigs in fasta or fna format.

Output:
Separate files or folders with genes and proteins (default) or only one of each.
Includes log and stats file (errors, exceptions, how many genes and proteins)
When output is multiple, includes single log file.

Example usage:

    python prodigal.py -i contigs/
    python prodigal.py -i contigs.fasta
"""

import os
import sys
import time
import argparse
import datetime
import subprocess
from helper_functions import is_fasta, is_fasta_wrapper


def is_fasta_wrapper(func):
    def wrapper(*args, **kwargs):
        if not is_fasta(args[0]):
            raise Exception(
                "Your file is not valid. Please check if it is a valid FASTA file."
            )
        func(args(*args, **kwargs))
    return wrapper


@is_fasta_wrapper
def prodigal(file, output=None):
    """
    Calls Prodigal on an input file.

    Input:
    Valid FASTA file.
    Output:
    Genes (.fna), proteins (.faa), gene scores (.txt), gbk file (.gbk).

    Example:

        from prodigal import prodigal
        prodigal("contigs.fasta", "output_folder/")

    """

    # if not is_fasta(file):
    #     raise Exception(
    #         "Your file is not valid. Please check if it is a valid FASTA file."
    #     )

    # Create default output format
    if not output:
        output = os.path.splitext(file)[0]
    else:
        output = os.path.join(output, os.path.basename(os.path.splitext(file)[0]))

    if not os.path.isdir(output):
        os.mkdir(output)

    output = os.path.join(output, output.split('/')[-1])

    prodigal = subprocess.call(
        f"prodigal -i {file} -a {output + '_proteins.faa'} \
        -d {output + '_genes.fna'} -o {output + '_cds.gbk'} \
        -s {output + '_scores.txt'} -q", shell=True
    )


if __name__ == "__main__":

    start = time.time()

    parser = argparse.ArgumentParser(description="""
    A script to call Prodigal to predict both genes and proteins.
    """)

    parser.add_argument("-i", "--input", help="Input FASTA file or dir containing fasta files")
    parser.add_argument("-o", "--output", help="Path to output folder",
                        default="")

    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        sys.exit(0)

    input = args.input

    if os.path.isfile(input):
        print(f"Starting script. Your input file is {input[0]}.")
        prodigal(input[0], args.output)

    elif os.path.isdir(input):

        files = os.listdir(input)
        files = [os.path.join(input, i) for i in files]
        files = [i for i in files if os.path.isfile(i)]

        print("\n")
        print(f"Starting script. You have {len(files)} files to be processed in {input}:\n")
        print("\n".join(files), "\n")

        success = 0
        failure = 0

        for i in files:
            try:
                print(f"Running Prodigal for {i}.")
                prodigal(i, args.output)
                if os.path.isdir(os.path.splitext(i)[0]):
                    success += 1
            except Exception as err:
                print(f"Error for {i}. Invalid FASTA file.")
                failure += 1
                pass
    else:
        raise FileNotFoundError

    end = time.time()
    delta = str(datetime.timedelta(seconds=end - start))

    print("\n")
    print(f"Done. {success} assemblies processed. {failure} errors. Took {delta}.")

"""
A file containing our main classes and functions.
# TODO: Create class for sets (geneset, protset)
"""

import datetime
import os
import time
from Bio import SeqIO
from bactools.bactools_helper import (
    get_records,
    is_fasta,
    is_fasta_wrapper,
    timer_wrapper,
)
from bactools.prodigal import prodigal
from bactools.prokka import prokka


class Assembly:
    """
    Assembly, a class containing bacterial assembly data and methods.

    # TODO: seqstats or Prodigal basic info (length, GC content) for metadata
    """

    def __init__(self, contigs=None, prodigal=False):
        super(Assembly, self).__init__()
        self.files = dict()
        self.metadata = None
        self.geneset = None
        self.protset = None

        if contigs:
            self.load_contigs(contigs)

        if prodigal:
            self.load_prodigal_input()

    def valid_contigs(self, quiet=True):
        if not self.files["contigs"]:
            raise Exception("Must specify input contigs file.")
        else:
            if not quiet:
                print("Your contig file is a valid FASTA file.")
            return True

    def load_contigs(self, contigs):
        """
        This loads the contigs input file. I want to make it a constructor method.
        """
        contigs = os.path.abspath(contigs)
        if not is_fasta(os.path.abspath(contigs)):
            raise Exception(
                "Your file is not valid. Please check if it is a valid FASTA file."
            )
        else:
            print(f"Contigs file set as {contigs}")
            self.files["contigs"] = os.path.abspath(contigs)

    def load_prodigal_input(
        self, prodigal_out=None, load_geneset=True, load_protset=True
    ):
        """
        Attach Prodigal results to class object.

        Input:
        prodigal_out is the output folder generated by the Prodigal function.
        """
        if prodigal_out:
            input = os.path.abspath(prodigal_out)
        else:
            try:
                if os.path.isdir(
                    os.path.splitext(os.path.abspath(self.files["contigs"]))[0]
                    + "_prodigal"
                ):
                    input = (
                        os.path.splitext(os.path.abspath(self.files["contigs"]))[0]
                        + "_prodigal"
                    )
                    print(f"Prodigal folder set as {input}")

            except Exception:
                print(
                    "Prodigal output folder not found. Please specify a valid Prodigal output folder."
                )

        # This dictionary is the same as output_files from the prodigal.py script.
        self.files["prodigal"] = dict()

        try:
            os.path.isdir(input)
        except FileNotFoundError:
            print(f"{prodigal_out} directory not found.")

        for file_ in os.listdir(input):
            file_ = os.path.join(input, file_)
            if file_.endswith("_genes.fna"):
                self.files["prodigal"]["genes"] = file_
            elif file_.endswith("_proteins.faa"):
                self.files["prodigal"]["proteins"] = file_
            elif file_.endswith("_cds.gbk"):
                self.files["prodigal"]["cds"] = file_
            elif file_.endswith("_scores.txt"):
                self.files["prodigal"]["scores"] = file_
            else:
                print(f"{file_} apparently is not a Prodigal output file. Ignoring it.")
                pass

        if load_geneset:
            self.load_geneset()
        if load_protset:
            self.load_protset()

    def load_geneset(self, kind="prodigal", records="list"):

        self.geneset = dict()

        if kind == "prodigal":
            # Origin is the file from which the set came from
            origin = self.files["prodigal"]["genes"]
            try:
                self.geneset["prodigal"] = dict()
                self.geneset["prodigal"]["records"] = get_records(origin, kind=records)
                self.geneset["prodigal"]["origin"] = origin

            except Exception:
                raise
        elif kind == "prokka":
            origin = self.files["prokka"]["genes"]
            try:
                self.geneset["prokka"] = dict()
                self.geneset["prokka"]["records"] = get_records(origin, kind=records)
                self.geneset["prokka"]["origin"] = origin
            except Exception:
                raise
        else:
            print(f"Passed {kind} kind of geneset input. Please specify a valid input.")

        # Maybe change this if/else block later.
        if self.geneset:
            if records == "list":
                print(
                    f"Loaded gene set from {kind.capitalize()} data. It has {len(self.geneset[kind]['records'])} genes."
                )
            else:
                print(f"Loaded gene set from {kind.capitalize()} data.")
        else:
            print(f"No gene set found in {origin}.")

    def load_protset(self, kind="prodigal", records="list"):

        self.protset = dict()

        if kind == "prodigal":
            origin = self.files["prodigal"]["proteins"]
            try:
                self.protset["prodigal"] = dict()
                self.protset["prodigal"]["records"] = get_records(origin, kind=records)
                # TODO: attach origin to a variable (stated by 'kind')
                self.protset["prodigal"]["origin"] = origin

            except Exception:
                raise
        # Add Prokka functionality here.
        # elif kind == "prokka":
        #     try:
        #         self.protset["prokka"] = dict()
        #         self.protset["prokka"]["proteins"] = get_records(
        #             self.files["prokka"]["proteins"], kind=records
        #         )
        #         self.protset["prokka"]["origin"] = self.files["prokka"]["proteins"]
        #     except Exception:
        #         raise
        elif kind == "prokka":
            origin = self.files["prokka"]["proteins"]
            try:
                self.protset["prokka"] = dict()
                self.protset["prokka"]["records"] = get_records(origin, kind=records)
                self.protset["prokka"]["origin"] = origin

            except Exception:
                raise

        if self.protset:
            if records == "list":
                print(
                    f"Loaded protein set from {kind.capitalize()} data. It has {len(self.protset[kind]['records'])} genes."
                )
            else:
                print(f"Loaded protein set from {kind.capitalize()} data.")
        else:
            print(f"No proteins set found in {origin}.")

    @timer_wrapper
    def run_prodigal(self, quiet=True):
        """
        Check for contigs file, run Prodigal on file.
        """
        self.valid_contigs(quiet)
        input = self.files["contigs"]
        print(
            f"Starting Prodigal. Your input file is {input}. Quiet setting is {quiet}."
        )
        prodigal_out = prodigal(input, quiet=quiet)
        self.files["prodigal"] = prodigal_out

    @timer_wrapper
    def run_prokka(self, quiet=True):
        """
        Check for contigs file, run Prokka on file.
        """
        self.valid_contigs(quiet)
        input = self.files["contigs"]
        print(f"Starting Prokka. Your input file is {input}. Quiet setting is {quiet}.")
        prokka_out = prokka(input)
        self.files["prokka"] = prokka_out


@is_fasta_wrapper
def load_from_fasta(contigs):
    """
    A function to load assemblies and run Prodigal directly.

    Input:
    A valid contigs file.

    Returns:
    An Assembly object.
    """
    assembly = Assembly()

    print(f"Loading contigs file from {contigs}.")
    assembly.load_contigs(contigs)
    assembly.run_prodigal()

    return assembly

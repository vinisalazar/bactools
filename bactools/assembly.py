"""
A file containing our main classes and functions.
# TODO: Create class for sets (geneset, protset)
"""

import os
import pandas as pd
import subprocess
from Bio import SeqIO
from bactools.bactools_helper import (
    get_records,
    is_fasta,
    is_fasta_wrapper,
    timer_wrapper,
)
from bactools.prodigal import Prodigal, run
from bactools.prokka import prokka


class Assembly:
    """
    Assembly, a class containing bacterial assembly data and methods.

    # TODO: seqstats or Prodigal basic info (length, GC content) for metadata
    """

    def __init__(self, contigs=None, prodigal=False):
        super(Assembly, self).__init__()
        self.directory = None
        self.files = dict()
        self.metadata = dict()
        self.geneset = dict()
        self.protset = dict()

        if contigs:
            self.load_contigs(contigs)

        if prodigal:
            self.load_prodigal()

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

        # Must use class decorator, same as in Prodigal class.
        if not is_fasta(os.path.abspath(contigs)):
            raise Exception(
                "Your file is not valid. Please check if it is a valid FASTA file."
            )
        else:
            self.files["contigs"] = os.path.abspath(contigs)
            print(f"Contigs file set as {contigs}")
            self.directory = os.path.dirname(self.files["contigs"])
            print(f"Directory set as {self.directory}")

    def load_seqstats(self):
        if not self.files["contigs"]:
            raise Exception(
                "Your Assembly doesn't have an input file! Please provide one."
            )

        self.metadata["seqstats"] = dict()

        try:
            stats = subprocess.check_output(["seqstats", self.files["contigs"]]).decode(
                "utf-8"
            )
            stats = stats.split("\n")
            for n in stats:
                n = n.split(":")
                if len(n) == 2:
                    try:
                        self.metadata["seqstats"][n[0]] = float(
                            n[1].strip().replace(" bp", "")
                        )
                    except (ValueError, IndexError) as error:
                        print(
                            "Something is wrong with the seqstats output. Please check your seqstats command."
                        )
        except FileNotFoundError:
            raise

    def seqstats(self):
        if self.metadata["seqstats"]:
            for key, value in self.metadata["seqstats"].items():
                print(f"{key}\t\t{value}")
        else:
            try:
                self.load_seqstats()
                self.seqstats
            except:
                print("Tried loading seqstats, but an error occurred.")
                raise

    def load_prodigal(self, prodigal_out=None, load_geneset=True, load_protset=True):
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
        """
        Loads gene sets unto Assembly.geneset.
        Uses the 'genes' key from the files[kind] dictionary.
        """
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
        if self.geneset[kind]:
            if records == "list":
                print(
                    f"Loaded gene set from {kind.capitalize()} data. It has {len(self.geneset[kind]['records'])} genes."
                )
            else:
                print(f"Loaded gene set from {kind.capitalize()} data.")
        else:
            print(f"No gene set found in {origin}.")

    def load_protset(self, kind="prodigal", records="list"):
        """
        Loads protein sets unto Assembly.protset.
        Uses the 'protein' key from the files[kind] dictionary.
        """
        if kind == "prodigal":
            origin = self.files["prodigal"]["proteins"]
            try:
                self.protset["prodigal"] = dict()
                self.protset["prodigal"]["records"] = get_records(origin, kind=records)
                # TODO: attach origin to a variable (stated by 'kind')
                self.protset["prodigal"]["origin"] = origin

            except Exception:
                raise
        elif kind == "prokka":
            origin = self.files["prokka"]["proteins"]
            try:
                self.protset["prokka"] = dict()
                self.protset["prokka"]["records"] = get_records(origin, kind=records)
                self.protset["prokka"]["origin"] = origin
            except Exception:
                raise

        if self.protset[kind]:
            if records == "list":
                print(
                    f"Loaded protein set from {kind.capitalize()} data. It has {len(self.protset[kind]['records'])} genes."
                )
            else:
                print(f"Loaded protein set from {kind.capitalize()} data.")
        else:
            print(f"No proteins set found in {origin}.")

    def fnoseqs(self, kind="prodigal", seqs="genes"):
        """
        Fast check of number of sequences in file.
        """
        with open(self.files[kind][seqs]) as f:
            records = SeqIO.parse(f, "fasta")
            len_ = sum(1 for x in records)

        return len_

    def sseqs(self, kind="prodigal", seqs="genes"):
        """
        Fast check of size of sequences file.
        """
        size = os.stat(self.files[kind][seqs]).st_size

        def format_bytes(
            size
        ):  # from https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb/37423778
            # 2**10 = 1024
            power = 2 ** 10
            n = 0
            power_labels = {0: "", 1: "k", 2: "m", 3: "g", 4: "t"}
            while size > power:
                size /= power
                n += 1

            return f"{round(size, 2)} {power_labels[n]}B"

        return format_bytes(size)

    @timer_wrapper
    def df_prodigal(self, kind="gene"):
        if not self.geneset["prodigal"]:
            try:
                self.load_geneset()
            except Exception("Please load your Prodigal geneset."):
                raise

        self.geneset["prodigal"]["df"] = pd.DataFrame(
            columns=(
                "id",
                "start",
                "stop",
                "strand",
                "id_",
                "partial",
                "start_type",
                "rbs_motif",
                "rbs_spacer",
                "gc_cont",
            )
        )

        def extract_row(record):
            row = record.description.split(";")
            row = row[0].split(" # ") + row[1:]
            row = [i.split("=")[-1] for i in row]
            return row

        for record in self.geneset["prodigal"]["records"]:
            # This one liner appends each record to the end of the dataframe.
            self.geneset["prodigal"]["df"].loc[
                len(self.geneset["prodigal"]["df"])
            ] = extract_row(record)

    @timer_wrapper
    def run_prodigal(self, quiet=True, load_sets=["gene", "prot"]):
        """
        Check for contigs file, run Prodigal on file.
        """
        self.valid_contigs(quiet)
        input = self.files["contigs"]
        output = os.path.dirname(os.path.abspath(self.files["contigs"]))
        print(
            f"Starting Prodigal. Your input file is {input}. Quiet setting is {quiet}."
        )
        prodigal_out = run(input, output=output, quiet=quiet)
        self.files["prodigal"] = prodigal_out
        if "gene" in load_sets:
            self.load_geneset()
        if "prot" in load_sets:
            self.load_protset()

    @timer_wrapper
    def run_prokka(self, quiet=True, load_sets=["gene", "prot"], **kwargs):
        """
        Check for contigs file, run Prokka on file.
        """
        self.valid_contigs(quiet)
        input = self.files["contigs"]
        print(f"Starting Prokka. Your input file is {input}. Quiet setting is {quiet}.")
        prokka_out = prokka(input, **kwargs)
        self.files["prokka"] = prokka_out
        if "gene" in load_sets:
            self.load_geneset("prokka")
        if "prot" in load_sets:
            self.load_protset("prokka")


@is_fasta_wrapper
def load_from_fasta(fasta_file):
    """
    A function to load assemblies and run Prodigal directly.

    Input:
    A valid contigs file.

    Returns:
    An Assembly object.
    """
    assembly = Assembly()

    print(f"Loading contigs file from {fasta_file}.")
    assembly.load_contigs(fasta_file)
    assembly.run_prodigal()

    return assembly

name = "bactools"

from bactools.assembly import Assembly, load_from_fasta
from bactools.bactools_helper import (
    get_records,
    is_fasta,
    is_fasta_wrapper,
    timer_wrapper,
)
from bactools.prodigal import Prodigal, prodigal
from bactools.prokka import prokka

from Bio import Entrez

"""
Parse gene_blaster.py outputs. We want the tabular blast output to be converted to include hit desc.
"""

Entrez.email = "viniws@gmail.com"  # This later will be on the settings file of Assembly tools.

handle = Entrez.efetch(id="WP_042849482.1", db="protein", rettype="gb", retmode="text")
print(handle.read())

help(Entrez.efetch)

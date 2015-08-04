#!/usr/bin/python

import time
import os
import sys
import argparse

# Copyright(C) 2015 David Ream
# Released under GPL version 3 licence. http://www.gnu.org/licenses/lgpl.html
# Do not remove this comment


#TODO:
# 1) remove all instances of operon, change language to reflect that we are working on gene blocks
# 2) add back the CD-hit functionality in "make_operon_query".  the coding is there, i just need to benchmark it against current results.
# 3) rename this script, to whatever makes some sense... i actually like it how it is.

#########################################################################################################################################
# I am putting some globals here, they are command line arguments for some of the scripts that we are using.  They are not				#
# important enough, at least at this time, to justify making them command line arguments for them.  This can be revised					#
# later, or changed by someone who cares too much about these trivial things. after we get everything running to our satisfaction.  	#
# Most likely all/almost all will be removed because it may tempt someone to ruin what already seems to be working well.				#
#########################################################################################################################################


#########################################################################################################
# regulondb_dl_parse.py:                                                                                #
# the only returned file we are interested in is the regulon_default_gene_block_file, defined below.    #
# it will be stored in the "regulonDB/" folder in the project outfolder that is supplied by the user.   #
#########################################################################################################

# NOTE: If a gene block file is supplied, this stage will be skipped. I curently do not perform a validity check on this input. 

# These options will not be alterable in the command line of this script, but have values that may be useful to control.
regulon_url = 'http://regulondb.ccg.unam.mx/menu/download/datasets/files/OperonSet.txt'
regulon_outfolder = 'regulonDB/'
regulon_default_gene_block_file = regulon_outfolder + 'operon_names_and_genes.txt'

# TODO: add this option as a command line arg for the gbeer standalone script
regulon_experimental_only = True

# What follows is a list of options that are controlled by user inputs to this script
# --infolder
# --outfolder
# --filter
# --num_proc
# --min_genes

# The download flag will not be set. If regulondb_dl_parse.py is invoked, it will download the regulon db file. 

#############################################################################################################
# create_newick_tree.py                                                                                     #
# This program has three outputs:                                                                           #
# a newick format phylogenetic tree - "out_tree.nwk"                                                        #
# a list of accession to commom names in the top down order of the created tree - "accession_to_common.csv" #
# a reordered filter file list for use later in the analysis - "phylo_order_new.txt"                        #
# these files will be stored in the tree/ directory of the project folder                                   #
#############################################################################################################

# TODO: 
# 1) add command line arg to allow a user to supply their own newick tree file.
# 1.5) if this option is included, i will need to call this script first.  Additionally, if both a filter and a tree file is provided, 
#      one will have to be preferred. I would choose the one generated by the tree file. Tree lables would need to conform to some specification.
# Tree creation has to have a better method available...  i need to search papers.
# 2) add command line arg to allow a user to supply their own marker gene.
# 2.5) When we add this option we need to make it possible to determine protein/RNA product, and then handle tree creation accordingly.
tree_marker_gene = "rpob"

# What follows is a list of options that are controlled by user inputs to this script
# --genbank_directory
# --filter

# This option will not be alterable in the command line of this script, but may be useful to control.
tree_outfolder = "tree/"

#############################################################################################################
# format_db.py:                                                                                             #
# This script creates a single output, a directory that contains all of the BLAST-searchable databases for  #
# use by blast_script.py in a later stage of this script.  Each database is named for the accession it was  #
# derived from.                                                                                             #
#############################################################################################################


# What follows is a list of options that are controlled by user inputs.
# --genbank_directory
# --outfolder
# --filter
# --num_proc

# TODO: nothing, other options are unlikely necessary for this stage. altering the DB type could be useful if we begin investigating RNA genes
# though currently this is not supported.

# These options will not be alterable in the command line of this script, but may be useful to control.
BLAST_database_folder = 'db/'
BLAST_format_protein = 'True'


#############################################################################################################
# make_operon_query.py:                                                                                     #
# This script produces a single output file that will serve as the BLAST query for the remainder of the     #
# project, stored in the project file as 'operon_query.fa'. Curently only one reference is used,            #
# but will expand to include more organisms automagically.                                                  #
#############################################################################################################


# not controlled by user inputs, but will be passed as a value to make_operon_query.py as a command line param for this script
refrence_organism = 'NC_000913' # will possibly deprecate in the future, in leu of an alternative approach
operon_query_outfile = 'operon_query.fa'


#############################################################################################################
# blast_script.py:                                                                                          #
# This script produces a tabular BLAST output per accession for the gene block query.                       #
#############################################################################################################

# What follows is a list of options that are controlled by user inputs.
# --filter
# --num_proc
# --query
# --eval

# Controlled by the output from a pervious step
# --database_folder

# not controlled by user inputs, but will be passed as a value to blast_script.py so the project folder is used.
BLAST_outfolder = 'blast_result/' # will be passed to --outfolder


#############################################################################################################
# blast_script.py:                                                                                          #
# This script produces a tabular BLAST output per accession for the gene block query.                       #
#############################################################################################################

# What follows is a list of options that are controlled by user inputs.
# --num_proc 

# Controlled by the output from a pervious step 
# --infolder    (in this case the bast_script.py output directory)
# --gene_block_query    (from make_operon_query.py)

# not controlled by user inputs, but will be passed as a value to blast_script.py so the project folder is used.
BLAST_parse_outfolder = 'blast_parse/'# will be passed to --outfolder

# not controlled by user inputs, no input is appropriate.  filter is for gene blocks that have been previously blasted, this option is to be run as a standalone option only.
# --filter


#############################################################################################################
# filter_operon_blast_results.py:                                                                           #
# This program will be used to remove spurious results from a BLAST search organized by gene block.         #
#############################################################################################################

# What follows is a list of options that are controlled by user inputs.
# --outfolder
# --num_proc
# --eval
# --max_gap

# not controlled by user inputs, but will be passed as a value to blast_script.py so the project folder is used.
filter_BLAST_parse_outfolder = 'optimized_gene_blocks/'# will be passed to --outfolder 

# not controlled by user inputs, no input is appropriate.  filter is for gene blocks that have been previously blasted, this option is to be run as a standalone option only.
# --filter

#############################################################################################################
# make_event_distance_matrix.py:                                                                            #
# This program will calculate the number of events that an organismal pair do not have in common.           #
#############################################################################################################

# What follows is a list of options that are controlled by user inputs.
# --gene_block_file   Though this could be generated by regulondb_dl_parse.py
# --num_proc
# --eval
# --max_gap

# Controlled by the output from a pervious step
# --infolder

# not controlled by user inputs, but will be passed as a value to blast_script.py so the project folder is used.
event_distance_outfolder = 'gene_block_distance_matrices/'# will be passed to --outfolder 

# not controlled by user inputs, no input is appropriate.  filter is for gene blocks that have been previously blasted, this option is to be run as a standalone option only.
# --operon_filter

#############################################################################################################
# operon_visual.py:                                                                                         #
# This program run all of the visualization scrips that make the results of the project easier to interpret.#
#############################################################################################################

# I will add a more detailed description of what this does, and requires once i figure it out myself.
visualization_outfolder = "visualization/"

# This exists to  make the main function easier to read. It contains code to run the argument parser, and does nothing else.
def parser_code():
    
    parser = argparse.ArgumentParser(description='The purpose of this script is to run the full software suite that we have developed to study operons using as few inputs as possible.  This will facilitate the ease of use as much as possible.')
    
    # This option needs to carry a dual default. There should be 'NONE' to denote that there was no input. Further, there should be a secondary default where
    # the regulondb_parse script will put the output file. The variable location of this file can be found in the 'regulondb_dl_parse.py command line args:' section.
    parser.add_argument("-i", "--gene_block_file", dest="gene_block_file", metavar="FILE", default='NONE',
                help="Input file for the gene block query step of the pipeline.")
    
    #parser.add_argument("-i", "--gene_block_file", dest="gene_block_file", metavar="FILE", default='./regulonDB/operon_names_and_genes.txt',
    #            help="Input file for the gene block query step of the pipeline.")
    
    #parser.add_argument("-I", "--infolder", dest="infolder", metavar="DIRECTORY", default='./genomes/',
    #            help="Folder containing all genbank files for use by the program.")
    
    parser.add_argument("-G", "--genbank_directory", dest="genbank_directory", metavar="DIRECTORY", default='./genomes/',
                help="Folder containing all genbank files for use by the program.")
                 
    parser.add_argument("-o", "--outfolder", dest="outfolder", metavar="DIRECTORY", default='./test_run/',
                help="Folder where results will be stored.")
    
    parser.add_argument("-f", "--filter", dest="filter", metavar="FILE", default='./phylo_order.txt',
                help="File restrictiong which accession numbers this script will process. If no file is provided, filtering is not performed.")
                
    parser.add_argument("-n", "--num_proc", dest="num_proc", metavar="INT", default = os.sysconf("SC_NPROCESSORS_CONF"), type=int,
                help="Number of processors that you want this script to run on. The default is every CPU that the system has.")

    parser.add_argument("-m", "--min_genes", dest="min_genes", metavar="INT", default = 5, type=int,
                help="Minum number of genes that an operon must contain before it can be considered for further analysis. The default is 5 because that is what we are currently using in the study.")
    
    parser.add_argument("-g", "--max_gap", dest="max_gap", metavar="INT", default = 500, type=int,
                help="Size in nucleotides of the maximum gap allowed between genes to be considered neighboring. The default is 500.")
               
    # turns out, passing this as a float will cause the eval threshold to always be 0.000000, which obviously causes issues        
    parser.add_argument("-e", "--eval", dest="eval", default='1e-10', metavar="FLOAT", #type=float,
                help="eval for the BLAST search.")
    
    # Currently a placeholder, but i will be adding this functionality soon.            
    parser.add_argument("-t", "--tree", dest="tree_file", metavar="FILE", default='NONE',
                help="Newick format tree file which will be used to bypass tree creation.")
    
    parser.add_argument("-c", "--clean", dest="clean", default=False, action='store_true',
                help="Flag to toggle the removal of intermediate files that are unnecessary for analysis, reducing the storage requirements for a run.")
                       
    return parser.parse_args()
    
    
def check_options(parsed_args):

    if parsed_args.gene_block_file == 'NONE' or os.path.exists(parsed_args.gene_block_file):
        gene_block_file = parsed_args.gene_block_file
    else:
        print "The file %s does not exist." % parsed_args.gene_block_file
        sys.exit()
    
    # check the genbank folder
    if os.path.isdir(parsed_args.genbank_directory):
        genbank_directory = parsed_args.genbank_directory
    else:
        print "The folder %s does not exist." % parsed_args.genbank_directory
        sys.exit()
    
    # if the directory that the user specifies does not exist, then the program makes it for them.
    # require that the folder name ends in a '/'
    if parsed_args.outfolder[-1] != '/':
       outfolder = parsed_args.outfolder + '/'
    else:
       outfolder = parsed_args.outfolder
    if not os.path.isdir(outfolder):
        os.makedirs(outfolder)
    print "outfolder", outfolder
    
    
    if parsed_args.filter == 'NONE' or os.path.exists(parsed_args.filter):
        filter_file = parsed_args.filter
    else:
        print "The file %s does not exist." % parsed_args.filter
        sys.exit()
   
    # section of code that deals determining the number of CPU cores that will be used by the program
    if parsed_args.num_proc > os.sysconf("SC_NPROCESSORS_CONF"):
        num_proc = os.sysconf("SC_NPROCESSORS_CONF")
    elif parsed_args.num_proc < 1:
        num_proc = 1
    else:
        num_proc = int(parsed_args.num_proc)
    
    if parsed_args.min_genes <= 0:
        min_genes = 1
    else:
        min_genes = parsed_args.min_genes
        
    # validate the input for the maximum allowed gap
    try:    
        max_gap = int(parsed_args.max_gap)
        if max_gap <= 0:
           print "The gap that you entered %s is a negative number, please enter a positive integer." % parsed_args.max_gap
           sys.exit()
        else:
           pass
    except:
        print "The gap that you entered %s is not an integer, please enter a positive integer." % parsed_args.max_gap
        sys.exit()
    
    # add these lines back in once i return the tree option to the program
    if parsed_args.tree_file == 'NONE' or os.path.exists(parsed_args.tree_file):
        tree_file = parsed_args.tree_file
    else:
        print "The file %s does not exist." % parsed_args.tree_file
        sys.exit()
    
        
    #e_val = float(parsed_args.eval)
    e_val = parsed_args.eval
    
    gene_block_file = parsed_args.gene_block_file
    
    clean = parsed_args.clean

    #return genbank_directory, gene_block_file, outfolder, filter_file, num_proc, min_genes, max_gap, e_val
    return genbank_directory, gene_block_file, outfolder, filter_file, num_proc, min_genes, max_gap, e_val, tree_file, clean

    
    
def main():
    
    start = time.time()

    parsed_args = parser_code()
    
    #genbank_directory, gene_block_file, outfolder, filter_file, num_proc, min_genes, max_gap, e_val = check_options(parsed_args)
    genbank_directory, gene_block_file, outfolder, filter_file, num_proc, min_genes, max_gap, e_val, tree_file, clean = check_options(parsed_args)
    
    #print genbank_directory, gene_block_file, outfolder, filter_file, num_proc, min_genes, max_gap, e_val
    print genbank_directory, gene_block_file, outfolder, filter_file, num_proc, min_genes, max_gap, e_val, tree_file, clean
    
    
    # checking new order for the script
    ########################################################
    # Step 2 fully checked and operational as of 7/21/2015 #
    ########################################################
    
    # Step 2: Create a phylogenetic tree from the organisms in the either the whole set provided in the genome directory, 
    # or from the organisms that are included in the organism filter file.  
    #TODO: 
    # 1) Make it possibel to choose a protein or RNA gene, currently only protein genes are accepted.
    # 2) Allow users to provide their own phylogenetic tree, and have the program use it, producing an accession list from the data if the tree lables are of a certain format
    #       2.1) options have been added to allow this.  the script needs to accomodate this option at this point.
    
    project_tree_outfolder = outfolder + tree_outfolder.lstrip("./")
    cmd2 = "./create_newick_tree.py --genbank_directory %s  --filter %s --outfolder %s --marker_gene %s" % (genbank_directory, filter_file, project_tree_outfolder, tree_marker_gene)
    #cmd2 = "./create_newick_tree.py --genbank_directory %s  -f %s" % (genbank_directory, filter_file)
    # print "cmd2", cmd2
    os.system(cmd2)
    '''
    
    '''    
    ########################################################
    # Step 1 fully checked and operational as of 7/13/2015 #
    ########################################################
    
    # Step 1: Get gene block set and parse into something that we can use
    # currently the default is to get operons from regulon db and use them as the gene neighborhoods we are searching for
    
    
    if gene_block_file == "NONE": # run the regulon script
        #now we need to set the output file for this stage
        project_regulon_outfolder = outfolder + regulon_outfolder
        print "project_regulon_outfolder ", project_regulon_outfolder 
        if regulon_experimental_only:
            cmd1 = "./regulondb_dl_parse.py -f %s -i %s -o %s -n %i -u %s -m %i" % (filter_file, genbank_directory, project_regulon_outfolder, num_proc, regulon_url, min_genes)
        else:
            cmd1 = "./regulondb_dl_parse.py -f %s -i %s -o %s -n %i -u %s -m %i --experimantal_only" % (filter_file, genbank_directory, project_regulon_outfolder, num_proc, regulon_url, min_genes)
    	print "cmd1", cmd1
    	
    	#cmd1 = "./regulondb_dl_parse.py -f phylo_order.txt"
    	os.system(cmd1)
    	gene_block_file = outfolder + regulon_default_gene_block_file
    	
    else: # do not run the regulon script, use the user-supplied file instead
        pass
    print "gene_block_file", gene_block_file
    
    
    ########################################################
    # Step 2 fully checked and operational as of 7/21/2015 #
    ########################################################
    
    # Step 2: Create a phylogenetic tree from the organisms in the either the whole set provided in the genome directory, 
    # or from the organisms that are included in the organism filter file.  
    #TODO: 
    # 1) Make it possibel to choose a protein or RNA gene, currently only protein genes are accepted.
    # 2) Allow users to provide their own phylogenetic tree, and have the program use it, producing an accession list from the data if the tree lables are of a certain format
    #       2.1) options have been added to allow this.  the script needs to accomodate this option at this point.
    
    project_tree_outfolder = outfolder + tree_outfolder.lstrip("./")
    cmd2 = "./create_newick_tree.py --genbank_directory %s  --filter %s --outfolder %s --marker_gene %s" % (genbank_directory, filter_file, project_tree_outfolder, tree_marker_gene)
    #cmd2 = "./create_newick_tree.py --genbank_directory %s  -f %s" % (genbank_directory, filter_file)
    # print "cmd2", cmd2
    os.system(cmd2)
    
    
    ########################################################
    # Step 3 fully checked and operational as of 7/23/2015 #
    ########################################################
    
    #Step 3: Create BLAST searchable databases. (I am limiting this to protein databases right now since that is what we do in the paper)
    project_BLAST_database_folder = outfolder + BLAST_database_folder
    cmd3 = "./format_db.py --filter %s --genbank_directory %s --outfolder %s --num_proc %i" % (filter_file, genbank_directory, project_BLAST_database_folder,  num_proc)
    
    # Set the database formatting option[Protein or DNA], even though we don't use it (yet).  verified working 7/22/2015
    if BLAST_format_protein == 'True':
        pass
    else:
        cmd3 = cmd3 + ' -d'
    print "cmd3", cmd3
    os.system(cmd3)
    
    
    
    #Step 4: make the operon query fasta file(s)
    operon_file = regulon_outfolder + 'operon_names_and_genes.txt'
    
    #This is the only outfile for this stage.  I don't think this needs its own seperate output directory, since this file is potentialy useful
    # to a user after the program is run.
    project_operon_query_outfile = outfolder + operon_query_outfile
    
    #cmd4 = "./make_operon_query.py -i %s -o %s -p %s -n %i -r %s" % (genbank_directory, operon_query_outfile, operon_file, num_proc, refrence_organism)
    cmd4 = "./make_operon_query.py -i %s -o %s -p %s -n %i -r %s" % (genbank_directory, project_operon_query_outfile, gene_block_file, num_proc, refrence_organism)
    print "cmd4", cmd4
    os.system(cmd4)
    
    
    ########################################################
    # Step 5 fully checked and operational as of 7/24/2015 #
    ########################################################
    
    #Step 5: run BLAST with the query that we made in stage 3, using the databases that we produced in stage 2.
    # TODO: 
    # make it possible to run this on an RNA database, though we have no use case for this currently.  This is of low priority.
    
    project_BLAST_outfolder = outfolder + BLAST_outfolder
    
    #cmd5 = "./blast_script.py -d %s -o %s -f %s -n %i -q %s -e %f" % (BLAST_database_folder, blast_outfolder, filter_file, num_proc, operon_query_outfile, e_val)
    #cmd5 = "./blast_script.py --database_folder %s --outfolder %s --filter %s --num_proc %i --query %s --eval %f" % (project_BLAST_database_folder, project_BLAST_outfolder, filter_file, num_proc, project_operon_query_outfile, e_val)
    
    #cmd5 = "./blast_script.py --database_folder %s --outfolder %s --filter %s --num_proc %i --query %s --eval %f" % (project_BLAST_database_folder, project_BLAST_outfolder, filter_file, num_proc, project_operon_query_outfile, e_val)
    cmd5 = "./blast_script.py --database_folder %s --outfolder %s --filter %s --num_proc %i --query %s --eval %s" % (project_BLAST_database_folder, project_BLAST_outfolder, filter_file, num_proc, project_operon_query_outfile, e_val)
    print "cmd5", cmd5
    os.system(cmd5)
    
    
    # Step 6: Parse the BLAST result and sort it by gene block
    
    project_BLAST_parse_outfolder = outfolder + BLAST_parse_outfolder 
    
    #cmd6 = "./blast_parse.py -f %s -n %i" % (filter_file, num_proc)
    #cmd6 = "./blast_parse.py --infolder %s --outfolder %s --gene_block_query %s --num_proc %i" % (project_BLAST_outfolder, project_BLAST_parse_outfolder, project_operon_query_outfile, num_proc)
    
    cmd6 = "./blast_parse.py --infolder %s --outfolder %s --gene_block_query %s --num_proc %i" % (project_BLAST_outfolder, project_BLAST_parse_outfolder, gene_block_file, num_proc)
    print "cmd6", cmd6
    os.system(cmd6)
    
    
    # Step 7: filter out spurious results and report the gene blocks that best represent the origional.
    
    project_filter_BLAST_parse_outfolder = outfolder +  filter_BLAST_parse_outfolder
    #cmd7 = "./filter_operon_blast_results.py -n %i -g %i" % (num_proc, max_gap)
    #cmd7 = "./filter_operon_blast_results.py --infolder %s --outfolder %s --num_proc %i --eval %f --max_gap %i" % (project_BLAST_parse_outfolder, project_filter_BLAST_parse_outfolder, num_proc, e_val, max_gap)
    cmd7 = "./filter_operon_blast_results.py --infolder %s --outfolder %s --num_proc %i --eval %s --max_gap %i" % (project_BLAST_parse_outfolder, project_filter_BLAST_parse_outfolder, num_proc, e_val, max_gap)
    print "cmd7", cmd7
    os.system(cmd7)
    
    
    ##########################################################################
    # seems to be running through step 8correctly no through testing yet.    #
    ##########################################################################
    
    # Step 8: determine z-scores for each value in the pairwaise event matrix that is calculated in step 7
    
    project_event_distance_outfolder = outfolder +  event_distance_outfolder
    
    # This input will need to be altered to explicity take in the file created in 7... but for now the default will do.
    #cmd8 = "./make_event_distance_matrix.py"
    cmd8 = "./make_event_distance_matrix.py --gene_block_file %s --infolder %s --outfolder %s --num_proc %i --max_gap %i" % (gene_block_file, project_filter_BLAST_parse_outfolder, project_event_distance_outfolder, num_proc, max_gap)
    print "cmd8", cmd8
    os.system(cmd8)
    
    '''
    # Step 9: Run the visualization pipelilne using the pairwaise event matrix that is calculated in step 7
    
    project_visualization_outfolder = outfolder + visualization_outfolder
    # during a normal run this code should not be necessary, but right now i'm having a problem and have to shove it in.
    if not os.path.isdir(project_visualization_outfolder):
        os.mkdir(project_visualization_outfolder)
    
    # this is the location of the various result files from create_newick_tree.py (might need to put this in step 2's documentation)
    project_mapping_file = project_tree_outfolder + "accession_to_common.csv"
    project_organism_reorder_file = project_tree_outfolder + "phylo_order_new.txt"
    # if a tree file is supplied by the user, this will have to be overridden with 
    project_tree_file = project_tree_outfolder + "out_tree.nwk"
    
    project_event_dict = project_event_distance_outfolder + "event_dict.p"
    
    # This input will need to be altered to explicity take in the file created in 7... but for now the default will do.
    #cmd9 = "./operonVisual.py -n ./optimized_operon/ -m ./mapping.csv -t ./out_tree.nwk -e ./event_dict.p -o ./visualization"
    #cmd9 = "./gbeerVisual/operonVisual.py -n ./gbeerVisual/data/optimized_operon/ -m ./gbeerVisual/data/mapping.csv -t ./gbeerVisual/data/reorder.nwk -e./gbeerVisual/data/event_dict.p -o ./visual"
    
    #cmd9 = "./operonVisual.py -n ./optimized_operon/ -m ./mapping.csv -t ./out_tree.nwk -e./event_dict.p -o ./visual"
    #cmd9 = "./operonVisual.py --OperonDataDirectory %s --MappingFile %s --NewickTree %s --EventsDict %s --OutputDirectory %s" % (project_event_distance_outfolder, project_mapping_file, project_tree_file, project_event_dict, project_visualization_outfolder)
    cmd9 = "./operonVisual.py --OperonDataDirectory %s --MappingFile %s --NewickTree %s --EventsDict %s --OutputDirectory %s" % (project_filter_BLAST_parse_outfolder, project_mapping_file, project_tree_file, project_event_dict, project_visualization_outfolder)
    
    print "cmd9", cmd9
    os.system(cmd9)
    '''
    
    
    print time.time() - start
    
if __name__ == '__main__':
    main()

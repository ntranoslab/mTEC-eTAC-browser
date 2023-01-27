
#----------------------------------Imports----------------------------------#
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import sqlalchemy as db
import math
import sys
import os
import getopt
import time
import warnings
warnings.simplefilter("ignore")

#---------------------------User defined settings---------------------------#
# Setup timer to track runtime
start_time = time.time()

# Default parameters
max_columns = 1000

# Set up required variables
data_file = None
database = None
host = None
user = None
passwd = None
save_path = None
metadata_cols = None

# Options
options = "f:d:s:u:p:o:m:c:h"
 
# usage
help = f'''
    mySQL_upload.py data -f data_path -d database -s host -u username -p password -o output_path -m metadata_cols [-c --columns] [-h --help]
    
    Uploads a table stored in a hdf5/csv file to a mySQL database        

    -f data_file_path
    --datafile data_file_path
        A file containing the table to be uploaded, saved using pandas
        
    -d database_name
    --database database_name
        The mySQL database name
    
    -s database_host
    --host database_host
        The mySQL database host

    -u username
    --user username
        The mySQL database username

    -p password
    --passwd passsword
        The mySQL database password

    -o output_path
    --output ouput_path
        The path to save the gene/table lookup dictionary
    
    -m metadata_col_list
    --metadata metadata_col_list
        A list of strings corresponding to the column names containing cell metadata in the data file (pass as list in format 'a,b,c,d')
    
    -c max_columns
    --columns max_columns
        The maximum number of columns in a mySQL table (default: 1000)

    -h 
    --help 
        print this message
    
'''

# Parsing argument
argv = sys.argv[1:]
arguments, values = getopt.getopt(argv, options)
# checking each argument
for argument, value in arguments:
    if argument in ("-f", "--datafile"):
        data_file = value
    elif argument in ("-d", "--database"):
        database = value
    elif argument in ("-s", "--host"):
        host = value
    elif argument in ("-u", "--user"):
        user = value
    elif argument in ("-p", "--passwd"):
        passwd = value
    elif argument in ("-o", "--output"):
        save_path = value
    elif argument in ("-m", "--metadata"):
        metadata_cols = value.split(",")
    elif argument in ("-c", "--columns"):
        max_columns = value
    elif argument in ("-h", "--help"):
        print(help)
        sys.exit()
    else:
        print(help)
        sys.exit()

req_vars = [data_file, database, host, user, passwd, save_path, metadata_cols]
# Check to make sure all required parameters are set
for var in req_vars:
    if var is None:
        print(help)
        sys.exit()
print()
print("=======================================================================")
print("----------------------mySQL scRNAseq data uploader---------------------")
print("=======================================================================")
print()
print("----------------------Setup---------------------")
print(f"Uploading data: {data_file}")
print(f"mySQL engine: mysql+pymysql://{user}:*****@{host}/{database}?local_infile=1")
print(f"Cell metadata: {metadata_cols}")

#----------------------------------Methods---------------------------------#
def sql_upload_csv(df, engine, table_name):
    # Create tmp.csv containing df to upload
    df.to_csv("tmp.csv", index_label="barcode")
    df = pd.read_csv("tmp.csv")
    # mapping of pandas column dtypes to mySQL data types
    dtype_map = {"float64": "DOUBLE", "object": "TINYTEXT", "int64": "MEDIUMINT"}
    col_string = []
    # iterate over columns in dataframe
    for i,column in enumerate(df.columns):
        # Get column dtype
        dtype = str(df.dtypes[i])
        # Add column name and dtype to column string list
        col_string.append(f"`{column}` {dtype}")
    # Convert col string list to single string
    col_string = ", ".join(col_string)
    # Replace column dtype with corresponding mySQL data type
    for initial, replace in dtype_map.items():
        col_string = col_string.replace(initial, replace)
    # Connect to database
    with engine.connect() as connection:
        # Drop the table if it already exists
        sql_query = f"DROP TABLE IF EXISTS {str(table_name)}"
        connection.execute(sql_query)
        # Create new table with columns/data types
        sql_query = f"CREATE TABLE {str(table_name)}({col_string})"
        connection.execute(sql_query)
        # Load temp csv into table
        sql_query = f"LOAD DATA LOCAL INFILE 'tmp.csv' REPLACE INTO TABLE {str(table_name)} FIELDS TERMINATED BY ',' IGNORE 1 ROWS"
        connection.execute(sql_query)
    # Cleanup tmp file
    os.remove("tmp.csv")

#------------------------------------Main----------------------------------#

##### Setup connection to mySQL server
engine = db.create_engine(f"mysql+pymysql://{user}:{passwd}@{host}/{database}?local_infile=1")
# Setup database (delete it if it exists and recreate it)
if database_exists(engine.url):
    print(f"Overwriting existing database named {database}")
    with engine.connect() as connection:
        # Drop the database if it already exists
        sql_query = f"DROP DATABASE IF EXISTS {database}"
        connection.execute(sql_query)
create_database(engine.url)
with engine.connect() as connection:
    sql_query = f"USE {database}"
    connection.execute(sql_query)
print()

print("---------------------Upload---------------------")
##### Prepare data from file
# Read hdf5 file (must have cells as rows and genes as columns with 'metadata_cols' added)
data = pd.read_hdf(data_file)
# Rename barcodes to be ints
data.index = [i for i in range(0, data.shape[0])]
# Get metadata to seperate df
metadata_df = data[metadata_cols]
# Subset on gene columns
data = data[data.columns[~data.columns.isin(metadata_df.columns)]]
# Remove gene columns that start with integer
data = data[data.columns[~data.columns.str.match('^\d')]]
# Remove gene columns that start with Gm
data = data[data.columns[~data.columns.str.startswith("Gm")]]
# Convert all column names to lowercase for easier matching
data.columns = data.columns.str.lower()

##### Upload tables to mySQL database
# Get all gene starting characters
gene_sets = set([i[0] for i in data.columns])
# Create dictionary mapping genes to their tables
gene_table_dict = {}
# Iterate over first characters
for letter in gene_sets:
    # Subset the gene dataframe on the current starting character
    gene_df = data[data.columns[data.columns.str.startswith(letter)]]
    print(f"Subsetting for gene table {letter}: num columns - {gene_df.shape[1]}")
    # If the subset df is greater than max column #
    if gene_df.shape[1] > max_columns:
        # Get the number of subtables needed to be under the max col number
        num_subtables = math.ceil(gene_df.shape[1]/max_columns)
        # Get the number of genes per subtable
        num_genes_per_subtable = round(gene_df.shape[1]/num_subtables)
        # Iterate over subtables
        for i in range(0, num_subtables):
            # If not the last subtable
            if i != num_subtables - 1:
                # Get the next batch of num_genes_per_subtable 
                subtable = gene_df.iloc[:,i*num_genes_per_subtable:(i+1)*num_genes_per_subtable]
            else:
                # Get the rest of the genes
                subtable = gene_df.iloc[:,i*num_genes_per_subtable:]
            print(f"\tSubtable {letter}{i}: num columns - {subtable.shape[1]}")
            # Save the gene to table mapping
            gene_mapping = dict(zip(subtable.columns, [f"{letter}{i}"]*len(subtable.columns)))
            gene_table_dict.update(gene_mapping)
            # Upload the subtable to the database
            sql_upload_csv(subtable, engine, f"{letter}{i}")
    else:
        # Save the gene to table mapping
        gene_mapping = dict(zip(gene_df.columns, [f"{letter}"]*len(gene_df.columns)))
        gene_table_dict.update(gene_mapping)
        # Upload the df to the database
        sql_upload_csv(gene_df, engine, letter)
# write metadata df to database
sql_upload_csv(metadata_df, engine, "cellmetadata")

##### Cleanup
print()
print("--------------------Cleanup---------------------")
# Save the gene table lookup dictionary as a csv
gene_table_df = pd.DataFrame(gene_table_dict, index=["table"]).T
print(f"Saving gene table lookup dictionary to {save_path}/{database}_gene_table_lookup.csv")
if save_path[-1] == "/":
    save_path = save_path[:-1]
gene_table_df.to_csv(f"{save_path}/{database}_gene_table_lookup.csv")
print(f"Upload complete, total runtime: {time.time() - start_time} s")
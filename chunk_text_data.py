# -*- coding: utf-8 -*-
"""
Created on Mon May 23 19:05:46 2022

@author: ipbilgin
"""
from pathlib import Path

import pandas as pd
import os



path_to_nq_data = "text.csv"
extracted_data_dir = "chunked_data"
data_index = 0
column_names = ["pmcid", "title", "keywords", "abstract", "body"]
chunksize = 20000 # default chunk size

def extract_chuncks(path_to_nq_data, chunksize,column_names):
    
    """.
    Extracts the chunks of data for the easeness of the investigation, load 
    and upload.  
    
    Args:
        path_to_nq_data: path to the text.csv
        
        chunksize: number of rows aimed to have in the chunked csv files. 
            
        column_names: name of the columns in text.csv
    
    """
    chunk_num = 0

    for chunk in pd.read_csv(path_to_nq_data, chunksize=chunksize):
        data_chunked = pd.DataFrame(columns=column_names)
        for num in range(chunksize):
            if not chunk["body"][num + (chunk_num * 20000)] == "  ":
                data_chunked = data_chunked.append(chunk.iloc[num])
    
        chunk_num = chunk_num + 1
        print(chunk_num)
        data_chunked = data_chunked.drop_duplicates(subset="pmcid", keep="first")
    
        corpus_file = Path(extracted_data_dir).joinpath(
            "metadata_" + str(chunk_num) + ".xlsx"
        )
        data_chunked.to_excel(corpus_file)  # convert to xlsx to keep the table format
    

def extract_the_last_chunck(path_to_nq_data):
    """.
    Extracts the last chunk from the main text.csv file where 
    the remaining number of rows are less then the original chunksize. 
    
    Args:
        path_to_nq_data: path to the text.csv
            
        column_names: name of the columns in text.csv
    
    """
    
    # change as it is required
    chunk_num = 18  # change this based on the remaining doc indx
    chunksize = 10490
    data_chunked = pd.DataFrame(columns=column_names)
    
    df = pd.read_csv(path_to_nq_data)
    data_chunked = pd.DataFrame(columns=column_names)
    
    for num in range(chunksize):
        if not df["body"][num + 340000] == "  ":
            data_chunked = data_chunked.append(df.iloc[num + 340000])
    
    data_chunked = data_chunked.drop_duplicates(subset="pmcid", keep="first")
    print("Data completed added")
    
    corpus_file = Path(extracted_data_dir).joinpath("metadata_" + str(chunk_num) + ".xlsx")
    data_chunked.to_excel(corpus_file)  # convert to xlsx to keep the table format
    


def convert_xlsx_to_csv(path_to_chunked_data):
    
    """.
    Converts the original xlsx format to csv format.
    
    Args:
        path_to_chunked_data: path to the text.csv
            
    
    """
    
    xlsx_files = os.listdir(path_to_chunked_data)
    
    for indx, file in enumerate(xlsx_files):
        file_path = Path(path_to_chunked_data) / file
        print(file_path)
        read_file = pd.read_excel(file_path, engine="openpyxl")
    
        # write into csv file
        read_file.to_csv(Path(path_to_chunked_data) / f"metadata_{indx}.csv", 
                         index=None, header=True
        )

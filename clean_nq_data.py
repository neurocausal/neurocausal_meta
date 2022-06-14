# -*- coding: utf-8 -*-
"""
Created on Mon May 23 19:05:46 2022

@author: ipbilgin
"""
import pandas as pd
from pathlib import Path


column_names = ["document-id", "pmid", "title","keywords","abstract","body"]

path_to_nq_data = 'neuroquery_corpus.csv'
extracted_data_dir = 'LOCAL_FOLDER'
# Extracts the 6 GB data into the chunks of xlsx format --> since csv screws with the unity of the body if the body text is not justified within the cell. 
# And spreads it into several lines. 

chunksize = 20000 # change as it is required
data_index=0
chunk_num=0
column_names = ["document-id", "pmid", "title","keywords","abstract","body"]

for chunk in pd.read_csv(path_to_nq_data, chunksize=chunksize):
    data_chunked = pd.DataFrame(columns = column_names)
    for num in range(chunksize):
        if not chunk['body'][num+(chunk_num*20000)] == '  ':
            data_chunked = data_chunked.append(chunk.iloc[num])
                
    chunk_num=chunk_num+1
    print(chunk_num)
    data_chunked=data_chunked.drop_duplicates(subset ="pmid",
                     keep = "first")
    
    corpus_file = Path(extracted_data_dir).joinpath('metadata_' + str(chunk_num) + '.xlsx')
    data_chunked.to_excel(corpus_file) # convert to xlsx to keep the table format 



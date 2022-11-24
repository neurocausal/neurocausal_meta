# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 16:33:35 2022

@author: ipbilgin
"""

import csv
import pandas as pd
from pathlib import Path
import numpy as np
import pubget

extracted_data_dir =  '\papers_passed_filter.csv'
papers_with_all_coordinates = '\coordinate_space.csv'

papers_with_all_coordinates_types = pd.read_csv(papers_with_all_coordinates)

papers_with_coordinates = papers_with_all_coordinates_types.loc[papers_with_all_coordinates_types['coordinate_space'] != 'UNKNOWN']

    
    


filtered_papers = pd.read_csv(extracted_data_dir)
filtered_papers_list = filtered_papers['5946103'].tolist()

df_list = papers_with_coordinates['pmcid'].tolist()

filtered_papers_with_MNI_coordinates = []
coordinate_type_all = []

coordinate_type_all = pd.DataFrame(columns=['pmcid', 'coordinate_space'])


for i in range(0,len(filtered_papers_list)):
    if filtered_papers_list[i] in df_list:
        filtered_papers_with_MNI_coordinates.append(filtered_papers_list[i])
        position = papers_with_all_coordinates_types.loc[papers_with_all_coordinates_types['pmcid'] == filtered_papers_list[i]]
        if (position['coordinate_space']== 'MNI').any() or (position['coordinate_space'] == 'TAL').any():
            coordinate_type_all =   coordinate_type_all.append(position)

coordinate_type_all.to_csv('\coordinate_type_all.csv', sep='\t', encoding='utf-8')



papers_with_TAL_coordinates = coordinate_type_all.loc[papers_with_all_coordinates_types['coordinate_space'] == 'TAL']
papers_with_MNI_coordinates = coordinate_type_all.loc[papers_with_all_coordinates_types['coordinate_space'] == 'MNI']

# conversion from TAL to MNI
#https://nimare.readthedocs.io/en/latest/generated/nimare.utils.tal2mni.html



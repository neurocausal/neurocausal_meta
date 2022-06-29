# -*- coding: utf-8 -*-
"""
Created on Fri June 17 11:47:46 2022

@author: FrancoisPgm
@author: IsilBilgin
"""
from math import floor
import regex as re
import argparse
import pandas as pd


CLINICAL_VOCAB = "clinical_vocabulary.txt"

TECHNICAL_VOCAB = "technical_vocabulary.txt"

def count_total_word_number(row):
    full_text = row["title"] + row["abstract"] + row["body"]
    total_word_number = len(re.findall(r'\w+', full_text))
    return total_word_number


def count_term_occurrence(row, word):
    total_word_number = count_total_word_number(row)
    full_text = row["title"] + row["abstract"] + row["body"]   
    if total_word_number != 0:
        n_matches = len(re.findall(word, full_text))
        return n_matches
    else:
         return 0

def search_clinical_vocab(row, vocab, word_thr, sum_thr):   
    n_matches = 0
    total_sum = 0
    full_text = row["title"] + row["abstract"] + row["body"]
    for word in vocab:
       n_matches += bool(re.search(word, full_text))
       if n_matches > word_thr:
        return True
       else:
           total_sum +=n_matches
           if total_sum > sum_thr:
                return True
    return False


def estimate_counts(vocab, texts_df):
    total_sum = 0
    #temp = 0
    for word in vocab:
        #print('Number of word iteration {}'.format(temp))
        #temp+=1
        word_count = texts_df.apply(
            count_term_occurrence, axis=1, args=(word,))
        texts_df[word] = word_count
        total_sum += word_count    
    texts_df["total_term_count"] = total_sum
    total_word_number = texts_df.apply(
     count_total_word_number, axis=1)
    
    texts_df["total_word_count"] = total_word_number
    #print("total word count {}". format(texts_df.loc[0].at["total_word_count"])  
    return texts_df


def density_of_clinical_terms(row):
    #print("total word count {}".format(row["total_word_count"]))
    if  row["total_word_count"] != 0:
        if ((row["total_term_count"] * 100) / row["total_word_count"] ) > 0.1:
            return True
        else:
            return False

def main(args):
    print('Reading file')
    texts_df = pd.read_csv(args.text_csv).fillna("")
    #print("Read {} lines".format(len(texts_df)))
    word_thr = args.word_threshold
    sum_thr = args.sum_threshold
    out_clinical_path = args.out_clinical_path if args.out_clinical_path is not None else args.text_csv.replace(
        "text.csv", "clinical.csv")
    out_technical_path = args.out_technical_path if args.out_technical_path is not None else args.text_csv.replace(
        "text.csv", "clinical.csv")
    
    
    # Filter the data based to clinical set using clinical_vocabulary.

    with open(CLINICAL_VOCAB, "r") as file:
        clinical_vocab = file.readlines()
        clinical_vocab = [word.rstrip() for word in clinical_vocab]
        
    print('Selection is running...') 
    texts_df["is_paper_clinical"] = texts_df.apply(
        search_clinical_vocab, axis=1, args=(clinical_vocab, word_thr, sum_thr))
    print('Selection is done')
    
    print('Clinical word counts are estimating...')
    texts_df = estimate_counts(clinical_vocab, texts_df)
    print('Clinical word counts are extracted.')
    
    texts_df["is_clinical_word_appearance_above_threshold"]  = texts_df.apply(density_of_clinical_terms, axis=1)
    print('Clinical word counts are estimated.')
    
    header = ["pmcid", "is_paper_clinical"] + clinical_vocab + ["total_term_count","total_word_count","is_clinical_word_appearance_above_threshold"]
    texts_df.to_csv(out_clinical_path, columns=header)
    print(f"Results saved in {out_clinical_path}")


    # Among the papers identified as clinical, search the technical term
    # occurrence.
    print('Technical word counts are estimating...')
    with open(TECHNICAL_VOCAB, "r") as file:
        tech_vocab = file.readlines()
        tech_vocab = [word.rstrip() for word in tech_vocab] 
    
    texts_df = texts_df[texts_df.is_paper_clinical == True]
    texts_df = estimate_counts(tech_vocab, texts_df)
    texts_df["is_technical_word_appearance_above_threshold"] = texts_df.apply(
        density_of_clinical_terms, axis=1)
    print('Technical word counts are estimated.')


    header = ["pmcid"] + \
        tech_vocab + ["total_term_count", "total_word_count","is_technical_word_appearance_above_threshold"]
    texts_df.to_csv(out_technical_path, columns=header)
    print(f"Results saved in {out_technical_path}")
    
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text_csv", "-t", type=str, required=True,
                        help="Path to the text.csv file containing the text of the paper from the nqdc extraction.")
    parser.add_argument("--word_threshold", "-w", type=int, required=True,
                        help="The threshold for the single keyword's appearance in a text.")
    parser.add_argument("--sum_threshold", "-s", type=int, required=True,
                        help="The threshold for total number of keyword appearances in a text.")
    parser.add_argument("--out_clinical_path", "-oc", type=str,
                        help="Output path for the csv file containing the pmcid and whether the paper is clinical.")
    parser.add_argument("--out_technical_path", "-ot", type=str,
                        help="Output path for the csv file containing the pmcid techical aspect of the data")
    args = parser.parse_args()
    main(args)
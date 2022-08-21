# -*- coding: utf-8 -*-
"""
Created on Fri June 17 11:47:46 2022

@author: FrancoisPgm
@author: IsilBilgin
"""
import regex as re
import argparse
import pandas as pd


VOC_PATH = "clinical_vocabulary.txt"
SUM_THRESHOLD = 200 # minimal number of different words from the vocabulary to find in a paper to consider it clinical
WORD_THRESHOLD = 10 # minimal number of different words from the vocabulary to find in a paper to consider it clinical


def count_clinical_words(row,word):
    word_match_count = []
    full_text = row["title"] + row["abstract"] + row["body"]
    n_matches = len(re.findall(word, full_text))
    return n_matches

def search_clinical_vocab(row, vocab):
    
    n_matches = 0
    total_sum = 0
    full_text = row["title"] + row["abstract"] + row["body"]
    for word in vocab:
       n_matches += bool(re.search(word, full_text))
       if n_matches > WORD_THRESHOLD:
        return True
       else:
           total_sum +=n_matches
           if total_sum > SUM_THRESHOLD:
                return True
    return False        

def main(args):
    texts_df = pd.read_csv(args.text_csv).fillna("")
    text_df_counting = texts_df
    out_path = args.out_path if args.out_path is not None else args.text_csv.replace("text.csv", "clinical.csv")
    with open(VOC_PATH, "r") as file:
        vocab = file.readlines()
        vocab = [word.rstrip() for word in vocab]
        vocab_string = [str(word) for word in vocab]
    texts_df["is_paper_clinical"] = texts_df.apply(search_clinical_vocab, axis=1, args=(vocab,))
    for word in vocab:
         texts_df[word] = texts_df.apply(count_clinical_words, axis=1, args=(word,))
    header  = ["pmcid", "is_paper_clinical"] + vocab_string
    texts_df.to_csv(out_path, columns=header)
    print(f"Results saved in {out_path}")
    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text_csv", "-t", type=str, required=True,
                        help="Path to the text.csv file containing the text of the paper from the nqdc extraction.")
    parser.add_argument("--out_path", "-o", type=str,
                        help="Output path for the csv file containing the pmcid and whether the paper is clinical.")
    args = parser.parse_args()
    main(args)

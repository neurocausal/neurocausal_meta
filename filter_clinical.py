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

VOC_PATH = "clinical_vocabulary.txt"

def count_total_word_number(row):
    full_text = row["title"] + row["abstract"] + row["body"]
    total_word_number = len(re.findall(r'\w+', full_text))
    return total_word_number

def count_clinical_words(row, word):
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


def main(args):
    print('Reading file')
    texts_df = pd.read_csv(args.text_csv).fillna("")
    print("Read {} lines".format(len(texts_df)))
    word_thr = args.word_threshold
    sum_thr = args.sum_threshold
    out_path = args.out_path if args.out_path is not None else args.text_csv.replace(
        "text.csv", "clinical.csv")
    print('Selection is running...')
    with open(VOC_PATH, "r") as file:
        vocab = file.readlines()
        vocab = [word.rstrip() for word in vocab]
    texts_df["is_paper_clinical"] = texts_df.apply(
        search_clinical_vocab, axis=1, args=(vocab, word_thr, sum_thr))
    print('Selection is done')
    total_sum = 0
    #print('Number of keywords {}'.format(len(vocab)))
    temp = 0
    for word in vocab:
        print('Number of word iteration {}'.format(temp))
        temp+=1
        word_count = texts_df.apply(
            count_clinical_words, axis=1, args=(word,))
        texts_df[word] = word_count
        total_sum += word_count    
    texts_df["total_term_count"] = total_sum
    total_word_number = texts_df.apply(
     count_total_word_number, axis=1)
    texts_df["total_word_count"] = total_word_number
    
    
    header = ["pmcid", "is_paper_clinical"] + \
        vocab + ["total_term_count",
                        "total_word_count"]
    texts_df.to_csv(out_path, columns=header)
    print(f"Results saved in {out_path}")
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text_csv", "-t", type=str, required=True,
                        help="Path to the text.csv file containing the text of the paper from the nqdc extraction.")
    parser.add_argument("--word_threshold", "-w", type=int, required=True,
                        help="The threshold for the single keyword's appearance in a text.")
    parser.add_argument("--vocabulary", "-v", type=str, required=True,
                        help="The vocabulary required for the search in the text.")
    parser.add_argument("--sum_threshold", "-s", type=int, required=True,
                        help="The threshold for total number of keyword appearances in a text.")
    parser.add_argument("--out_path", "-o", type=str,
                        help="Output path for the csv file containing the pmcid and whether the paper is clinical.")
    args = parser.parse_args()
    main(args)
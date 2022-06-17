# -*- coding: utf-8 -*-
"""
Created on Fri June 17 11:47:46 2022

@author: FrancoisPgm
"""
import regex
import argparse
import pandas as pd


VOC_PATH = "clinical_vocabulary.txt"
THRESHOLD = 20 # minimal number of different words from the vocabulary to find in a paper to consider it clinical


def search_clinical_vocab(row, vocab):
    n_matches = 0
    full_text = row["title"] + row["abstract"] + row["body"]
    for word in vocab:
        n_matches += bool(regex.search(word, full_text))
        if n_matches > THRESHOLD:
            return True
    return False


def main(args):
    texts_df = pd.read_csv(args.text_csv).fillna("")
    out_path = args.out_path if args.out_path is not None else args.text_csv.replace("text.csv", "clinical.csv")
    with open(VOC_PATH, "r") as file:
        vocab = file.readlines()
        vocab = [word.rstrip() for word in vocab]
    texts_df["clinical"] = texts_df.apply(search_clinical_vocab, axis=1, args=(vocab,))
    texts_df.to_csv(out_path, columns=["pmcid", "clinical"])
    print(f"Results saved in {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text_csv", "-t", type=str, required=True,
                        help="Path to the text.csv file containing the text of the paper from the nqdc extraction.")
    parser.add_argument("--out_path", "-o", type=str,
                        help="Output path for the csv file containing the pmcid and wether the paper is clinical.")
    args = parser.parse_args()
    main(args)


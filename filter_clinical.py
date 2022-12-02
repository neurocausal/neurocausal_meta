# -*- coding: utf-8 -*-
"""
Created on Fri June 17 11:47:46 2022

@author: FrancoisPgm
@author: IsilBilgin
"""
'''
The usage of the call is python filter_clinical.py --text_csv meta_analysis.csv  --out_clinical_path metadata_clinical_all.csv --out_technical_path metadata_technical_all.csv
'''

from math import floor
import regex as re
import argparse
import pandas as pd

CLINICAL_VOCAB = "clinical_vocabulary.txt"

TECHNICAL_VOCAB = "technical_vocabulary.txt"

EXCLUDE_VOCAB = "exclude_vocabulary.txt"


def count_total_word_number(row):
    full_text = row["title"] + row["abstract"] + row["body"]
    total_word_number = len(re.findall(r'\w+', full_text))
    return total_word_number


def count_term_occurrence(row, word):
    total_word_number = count_total_word_number(row)
    full_text = row["title"] + row["abstract"] + row["body"]
    if total_word_number > 400:
        n_matches = len(re.findall(word, full_text))
        return n_matches
    else:
        return 0


def estimate_counts(vocab, texts_df):
    total_sum = 0
    # temp = 0
    for word in vocab:
        # print('Number of word iteration {}'.format(temp))
        # temp+=1
        word_count = texts_df.apply(
            count_term_occurrence, axis=1, args=(word,))
        texts_df[word] = word_count
        total_sum += word_count
    texts_df["total_term_count"] = total_sum
    total_word_number = texts_df.apply(
        count_total_word_number, axis=1)

    texts_df["total_word_count"] = total_word_number
    # print("total word count {}". format(texts_df.loc[0].at[
    # "total_word_count"])
    return texts_df


def density_of_clinical_terms(row):
    # print("total word count {}".format(row["total_word_count"]))
    if row["total_word_count"] != 0:
        if ((row["total_term_count"] * 100) / row["total_word_count"]) > 0.3:
            return True
        else:
            return False


def percentage_of_clinical_terms(row):
    # print("total word count {}".format(row["total_word_count"]))
    if row["total_word_count"] != 0:
        perc = row["total_term_count"] * 100 / row["total_word_count"]
    return perc


def remove_redundant_data(texts_df):
    for index, row in texts_df.iterrows():
        if row["total_word_count"] < 400:
            texts_df.drop(index, inplace=True)
    return texts_df


def main(args):
    print('Reading file')
    texts_df = pd.read_csv(args.text_csv).fillna("")
    # print("Read {} lines".format(len(texts_df)))
    out_clinical_path = args.out_clinical_path if args.out_clinical_path is not None else args.text_csv.replace(
        "text.csv", "clinical.csv")
    out_technical_path = args.out_technical_path if args.out_technical_path is not None else args.text_csv.replace(
        "text.csv", "clinical.csv")
    out_excl_path = args.out_excl_path if args.out_excl_path is not None else args.text_csv.replace(
        "text.csv", "clinical.csv")

    # Filter the data based to clinical set using clinical_vocabulary.

    with open(CLINICAL_VOCAB, "r") as file:
        clinical_vocab = file.readlines()
        clinical_vocab = [word.rstrip() for word in clinical_vocab]

    print('Clinical word counts are estimating...')
    texts_df = estimate_counts(clinical_vocab, texts_df)
    print('Clinical word counts are extracted.')

    texts_df["is_clinical_word_appearance_above_threshold"] = texts_df.apply(
        density_of_clinical_terms, axis=1)
    print('Clinical word counts are estimated.')

    texts_df = remove_redundant_data(texts_df)

    header = ["pmcid"] + clinical_vocab + ["total_term_count",
                                           "total_word_count",
                                           "is_clinical_word_appearance_above_threshold"]
    texts_df.to_csv(out_clinical_path, columns=header)
    print(f"Results saved in {out_clinical_path}")

    # Among the papers identified as clinical, search the technical term
    # occurrence.
    print('Technical word counts are estimating...')
    with open(TECHNICAL_VOCAB, "r") as file:
        tech_vocab = file.readlines()
        tech_vocab = [word.rstrip() for word in tech_vocab]

        # texts_df = texts_df[texts_df.is_paper_clinical == True]
    texts_df = estimate_counts(tech_vocab, texts_df)
    texts_df["is_technical_word_appearance_above_threshold"] = texts_df.apply(
        density_of_clinical_terms, axis=1)
    print('Technical word counts are estimated.')

    header = ["pmcid"] + \
             tech_vocab + ["total_term_count", "total_word_count",
                           "is_technical_word_appearance_above_threshold"]
    texts_df.to_csv(out_technical_path, columns=header)
    print(f"Results saved in {out_technical_path}")

    # Among the technical papers, search the exclude term
    # occurrence.
    print('Exclude word counts are estimating...')
    with open(EXCLUDE_VOCAB, "r") as file:
        exclude_vocab = file.readlines()
        exclude_vocab = [word.rstrip() for word in exclude_vocab]

        # texts_df = texts_df[texts_df.is_paper_clinical == True]
    texts_df = estimate_counts(exclude_vocab, texts_df)
    texts_df["exclusion_perc"] = texts_df.apply(
        percentage_of_clinical_terms, axis=1)
    print('Exclude word counts are estimated.')

    with open(CLINICAL_VOCAB, "r") as file:
        clinical_vocab = file.readlines()
        clinical_vocab = [word.rstrip() for word in clinical_vocab]

        # texts_df = texts_df[texts_df.is_paper_clinical == True]
    texts_df = estimate_counts(clinical_vocab, texts_df)
    texts_df["clinical_perc"] = texts_df.apply(
        percentage_of_clinical_terms, axis=1)
    print('Clinical word counts are estimated.')

    header = ["pmcid", "exclusion_perc", "clinical_perc"]
    texts_df.to_csv(out_excl_path, columns=header)
    print(f"Results saved in {out_excl_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text_csv", "-t", type=str, required=True,
                        help="Path to the text.csv file containing the text "
                             "of the paper from the nqdc extraction.")
    parser.add_argument("--out_clinical_path", "-oc", type=str,
                        help="Output path for the csv file containing the "
                             "pmcid and whether the paper is clinical.")
    parser.add_argument("--out_technical_path", "-ot", type=str,
                        help="Output path for the csv file containing the "
                             "pmcid techical aspect of the data")
    parser.add_argument("--out_excl_path", "-oe", type=str,
                        help="Output path for the csv file containing the "
                             "pmcid excl aspect of the data")
    args = parser.parse_args()
    main(args)

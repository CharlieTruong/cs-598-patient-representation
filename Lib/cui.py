"""Process patient clinical notes to Concept Unique Identifiers (CUI)"""
import argparse
import os
from concurrent.futures import as_completed, ProcessPoolExecutor
from typing import List, Optional

import numpy as np
import pandas as pd
from medcat.cat import CAT
from medcat.cdb import CDB
from medcat.meta_cat import MetaCAT
from medcat.vocab import Vocab


MEDCAT_CDB_PATH = os.path.abspath("Lib/med_cat_model/cdb.dat")
MEDCAT_SPACY_MODEL_PATH = os.path.abspath("Lib/med_cat_model/spacy_model")
MEDCAT_VOCAB_PATH = os.path.abspath("Lib/med_cat_model/vocab.dat")
MEDCAT_STATUS_PATH = os.path.abspath("Lib/med_cat_model/meta_Status")


def parse_mimic_iii_notes(notes_file: str, limit: Optional[int] = None) -> pd.DataFrame:
    """Return a dataframe of notes from the MIMIC-III dataset

    Args:
        notes_file: The path to the csv notes file
        limit: A limit on the records to read from the file

    Returns:
        A dataframe of the notes with the columns subject_id,notes
    """
    df = pd.read_csv(notes_file, usecols=["SUBJECT_ID", "TEXT"], nrows=limit)
    df.columns = df.columns.str.lower()
    return df.groupby("subject_id")["text"].apply(lambda x: " ".join(x)).reset_index()


def parse_i2b2_notes(notes_file: str, limit: Optional[int] = None) -> pd.DataFrame:
    """Return a dataframe of notes from the I2B2 dataset

    Args:
        notes_file: The path to the xml notes file
        limit: A limit on the records to read from the file

    Returns:
        A dataframe of the notes with the columns subject_id,notes
    """
    with open(notes_file) as f:
        df = pd.read_xml(f.read(), xpath=".//doc")
        if limit is not None:
            df = df.head(limit)

    df = df.rename(columns={"id": "subject_id"})
    return df


def save_notes_by_patient(notes_df: pd.DataFrame, output_dir: str):
    """Save a dataframe of patient notes to a directory

    Each patient's notes will be saved as a separate file

    Args:
        notes_df: A dataframe of patient notes
        output_dir: The output directory
    """
    for _, row in notes_df.iterrows():
        with open(f"{output_dir}/{row['subject_id']}.txt", "w") as f:
            f.write(row["text"])


def extract_patient_group_cuis(input_files: List[str], output_dir):
    """Extract the CUIs for a group of patient notes

    This is intended to run with multiprocessing

    Args:
        input_files: The list of patient files to process
        output_dir: The output directory
    """
    vocab = Vocab.load(MEDCAT_VOCAB_PATH)
    cdb = CDB.load(MEDCAT_CDB_PATH, config_dict={"general": {"spacy_model": MEDCAT_SPACY_MODEL_PATH, "spell_check": False, "workers": 1}})
    mc_status = MetaCAT.load(MEDCAT_STATUS_PATH)
    MEDCAT = CAT(cdb=cdb, config=cdb.config, vocab=vocab, meta_cats=[mc_status])
    for input_file in input_files:
        with open(input_file) as f:
            entities = MEDCAT.get_entities(f.read())["entities"]
            cuis = " ".join(e['cui'] for e in entities.values())
            filename = os.path.basename(input_file)
            with open(f"{output_dir}/{filename}", "w") as f:
                f.write(cuis)


def extract_all_patient_cuis(input_dir: str, output_dir: str, max_workers: Optional[int] = 1):
    """Map patient clinical notes to CUIs and export to a directory

    Args:
        input_dir: A directory containing the raw clinical notes per patient
        output_dir: The output directory
        max_workers: The max number of workers to use to extract the CUIs

    """
    input_files = [
        f"{input_dir}/{f}" for f in os.listdir(input_dir)
        if f.endswith(".txt") and not os.path.exists(f"{output_dir}/{f}")
    ]
    input_file_chunks = np.array_split(input_files, max_workers)
    with ProcessPoolExecutor(max_workers=max_workers) as e:
        futures = [e.submit(extract_patient_group_cuis, chunk, output_dir) for chunk in input_file_chunks]

        # Ensure an error is raised to stop processing if any of the workers fail
        for future in as_completed(futures):
            future.result()


def parse_ctakes_cuis(input_dir: str, output_dir: str):
    """Parse files from ctakes and output to another directory

    Args:
        input_dir: The directory containing the ctakes output. There will be a file per patient,
            and the file is a pipe delimited file of CUI counts
        output_dir: The directory where to save the parsed file. This will be a file per patient
            with the CUIs separated by a space
    """
    for f in os.listdir(input_dir):
        df = pd.read_csv(f"{input_dir}/{f}", sep="|", header=None, names=["cui", "count"])
        df["cui_extended"] = ((df["cui"] + " ") * df["count"]).str.strip()
        output_filename = f"{f.split('.')[0]}.txt"
        with open(f"{output_dir}/{output_filename}", "w") as f:
            f.write(" ".join(df["cui_extended"]))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract CUIs from patient notes")
    parser.add_argument(
        "command",
        help="The command to execute",
        choices=["extract_notes", "extract_cuis", "parse_ctakes_cuis"],
        type=str
    )
    parser.add_argument(
        "--notes_file_path",
        help="The file path to the notes file",
        default="MimicIII/Source/NOTEEVENTS.csv",
        type=str
    )
    parser.add_argument(
        "--limit",
        help="The number of note records to extract",
        default=None,
        type=int
    )
    parser.add_argument(
        "--text_input_dir",
        help="The directory path containing the raw notes per patient",
        default="MimicIII/Patients/Notes",
        type=str
    )
    parser.add_argument(
        "--output_dir",
        help="The path where to output the extracted CUIs",
        default="MimicIII/Patients/Notes",
        type=str
    )
    parser.add_argument(
        "--dataset_source",
        help="The dataset source name",
        type=str,
        default="mimic_iii",
        choices=["mimic_iii", "i2b2"]
    )
    parser.add_argument(
        "--max_workers",
        help="The max workers to use for extracting CUIs",
        type=int,
        default=1
    )
    args = parser.parse_args()
    parse_funcs = {"mimic_iii": parse_mimic_iii_notes, "i2b2": parse_i2b2_notes}
    if args.command == "extract_notes":
        notes_df = parse_funcs[args.dataset_source](args.notes_file_path, limit=args.limit)
        save_notes_by_patient(notes_df, args.output_dir)
    elif args.command == "extract_cuis":
        extract_all_patient_cuis(args.text_input_dir, args.output_dir, max_workers=args.max_workers)
    elif args.command == "parse_ctakes_cuis":
        parse_ctakes_cuis(args.text_input_dir, args.output_dir)

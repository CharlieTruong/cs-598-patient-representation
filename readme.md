# CS-598 Patient Representation - Spring 2023

This is a fork of [this repo](https://github.com/dmitriydligach/starsem2018-patient-representations), which contains code for the paper [Learning Patient Representation from Text](https://aclanthology.org/S18-2014.pdf) by Dmitriy Dligach and Timothy Miller.

This project aims to replicate the results from the paper to better understand it and add some additional scenarios that were not originally conducted.

## Project Team Members

* Nabeel Mamoon (nmamoon2)
* Charlie Truong (ctruong4)

## CUI Extraction

The original code did not have any code associated with extracting the Concept Unique Identifiers (CUI). The paper authors used [Apache Ctakes](https://ctakes.apache.org/). However, we opted to use the [Medcat package](https://github.com/CogStack/MedCAT) to fully define the extraction with a Python script. The script is defined at `Lib/cui` and has two commands with the following arguments:

* `python Lib/cui.py extract_notes` - Extracts patient notes from an aggregated file into individual files
    * `--notes_file_path` - The path of the aggregated notes file such as `MimicIII/Source/NOTEEVENTS.csv`
    * `--output_dir` - The directory where the notes should be exported such as `"MimicIII/Patients/Notes`
    * `--dataset_source` - This will be either `i2b2` or `mimic_iii`. This determines how to parse the aggregated file since the `i2b2` data is xml and the `mimic_iii` data is a csv.
    * `--limit` - Optionally, this can be passed to limit the number of records to parse

* `python Lib/cui.py extract_cuis` - Extracts CUIs from individual patient notes
    * `--text_input_dir` - The directory containing individual notes such as `MimicIII/Patients/Notes`
    * `--output_dir` - The directory where the extracted CUIs should be exported such as `"MimicIII/Patients/Cuis`
    * `--max_workers` - The extraction process can be slow so this allows running the extraction with multiprocessing. The default value is 1.

The notes must be extracted first via `extract_notes` and then `extract_cuis` can be used. This all assumes that the following data exists:

* `MimicIII/Source/NOTEEVENTS.csv` - This is the aggregated clinical notes from the [MIMIC III dataset](https://physionet.org/content/mimiciii/1.4/)
* `Comorbidity/Xml/obesity_patient_records_training.xml` - Part 1 of the training data from the [I2B2 obesity dataset](https://portal.dbmi.hms.harvard.edu/projects/n2c2-nlp/)
* `Comorbidity/Xml/obesity_patient_records_training2.xml` - Part 2 of the training data from the I2B2 obesity dataset
* `Comorbidity/Xml/obesity_patient_records_test.xml` - The test data from the I2B2 obesity dataset

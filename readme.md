# CS-598 Patient Representation - Spring 2023

This is a fork of [this repo](https://github.com/dmitriydligach/starsem2018-patient-representations), which contains code for the paper [Learning Patient Representation from Text](https://aclanthology.org/S18-2014.pdf) by Dmitriy Dligach and Timothy Miller.

This project aims to replicate the results from the paper to better understand it and add some additional scenarios that were not originally conducted.

## Project Team Members

* Nabeel Mamoon (nmamoon2)
* Charlie Truong (ctruong4)

## Data Directories

If running code in this repo for the first time, the following directories will need to be added to the repo:

* Codes/Model - This will contain the trained model for CUI embeddings and associated metadata
* Comorbidity/Cuis/Test - This will contain the extracted CUIs from the test data in the I2B2 dataset
* Comorbidity/Cuis/Train1+2 - This will contain the extracted CUIs from the training data in the I2B2 dataset
* Comorbidity/Notes/Test - This will contain the raw text test data per patient from the I2B2 dataset
* Comorbidity/Notes/Train1+2 - This will contain the raw text training data per patient from the I2B2 dataset
* Comorbidity/Model - This will contain the metadata from training the SVM model with a sparse representation of the codes
* Comorbidity/Xml - This contains the raw XML data from the I2B2 dataset:
    * obesity_patient_records_test.xml
    * obesity_patient_records_training.xml
    * obesity_patient_records_training2.xml
    * obesity_standoff_annotations_test_intuitive.xml
    * obesity_standoff_annotations_training_addendum3.xml
    * obesity_standoff_annotations_training.xml
* MimicIII/Patients/Cuis - This will contain the extracted CUI data from the raw text
* MimicIII/Patients/Notes - This will contain the raw text data per patient
* MimicIII/Source - This should contain raw data from MIMIC-III: CPTEVENTS.csv, DIAGNOSES_ICD.csv, NOTEEVENTS.csv, PROCEDURES_CID.csv

## CUI Extraction

The original code did not have any code associated with extracting the Concept Unique Identifiers (CUI). The paper authors used [Apache cTAKES](https://ctakes.apache.org/).

In order to fully use cTAKES, you must first obtain a [UMLS License](https://www.nlm.nih.gov/databases/umls.html) from the National Library of Medicine. Then you should download and [install cTAKES](https://cwiki.apache.org/confluence/display/CTAKES/cTAKES+4.0+User+Install+Guide). The default pipeline is very slow to extract CUIs. Instead, we have defined a modified pipeline in the file `cui.piper`.

Before running the pipeline, extract the raw text for both MIMIC-III and I2B2 dataset to their appropriate directories using this script:

* `python Lib/cui.py extract_notes` - Extracts patient notes from an aggregated file into individual files
    * `--notes_file_path` - The path of the aggregated notes file such as `MimicIII/Source/NOTEEVENTS.csv`
    * `--output_dir` - The directory where the notes should be exported such as `"MimicIII/Patients/Notes`
    * `--dataset_source` - This will be either `i2b2` or `mimic_iii`. This determines how to parse the aggregated file since the `i2b2` data is xml and the `mimic_iii` data is a csv.
    * `--limit` - Optionally, this can be passed to limit the number of records to parse

To run the pipeline, here is an example command:

```
/usr/local/apache-ctakes/bin/runPiperFile.sh -p /path/to/cui.piper  --key <your-umls-api-key>
```

The `cui.piper` file will need to be modified based on the input and output directories.

### Alternative to cTAKES - Medcat

Before receiving our UMLS license, we attempted to use the [Medcat package](https://github.com/CogStack/MedCAT) to fully define the extraction with a Python script. However, the initial results did not meet our expectations. The script is defined at `Lib/cui` with the following arguments:

* `python Lib/cui.py extract_cuis` - Extracts CUIs from individual patient notes
    * `--text_input_dir` - The directory containing individual notes such as `MimicIII/Patients/Notes`
    * `--output_dir` - The directory where the extracted CUIs should be exported such as `"MimicIII/Patients/Cuis`
    * `--max_workers` - The extraction process can be slow so this allows running the extraction with multiprocessing. The default value is 1.

The notes must be extracted first via `extract_notes` and then `extract_cuis` can be used. This all assumes that the following data exists:

* `MimicIII/Source/NOTEEVENTS.csv` - This is the aggregated clinical notes from the [MIMIC III dataset](https://physionet.org/content/mimiciii/1.4/)
* `Comorbidity/Xml/obesity_patient_records_training.xml` - Part 1 of the training data from the [I2B2 obesity dataset](https://portal.dbmi.hms.harvard.edu/projects/n2c2-nlp/)
* `Comorbidity/Xml/obesity_patient_records_training2.xml` - Part 2 of the training data from the I2B2 obesity dataset
* `Comorbidity/Xml/obesity_patient_records_test.xml` - The test data from the I2B2 obesity dataset

## Training Models

To train the CUI model, navigate to the `Codes` directory and run this command:

```
python ft.py cuis.cfg
```

Then to train the SVM model with a sparse representation, navigate to the `Comorbidity` directory and run this command:

```
python svm.py sparse.cfg
```

Then to train the SVM model with the CUI embedding, navigate to the `Comorbidity` directory and run this command:

```
python svm.py dense.cfg
```

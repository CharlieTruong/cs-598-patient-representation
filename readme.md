# CS-598 Patient Representation - Spring 2023

This is a fork of [this repo](https://github.com/dmitriydligach/starsem2018-patient-representations), which contains code for the paper [Learning Patient Representation from Text](https://aclanthology.org/S18-2014.pdf) by Dmitriy Dligach and Timothy Miller.

This project aims to replicate the results from the paper to better understand it and add some additional scenarios that were not originally conducted.

## Project Team Members

* Nabeel Mamoon (nmamoon2)
* Charlie Truong (ctruong4)

## Data Download

Here is the data used in this project:

* MIMIC-III - De-identified health data for ~40K patients available on [Physionet](https://physionet.org/content/mimiciii/1.4/). In order to access the data, you must first apply to be a [credentialed user](https://physionet.org/login/?next=/settings/credentialing/). Here is the data you need to download:

    * [CPTEVENTS.csv](https://physionet.org/content/mimiciii/1.4/CPTEVENTS.csv.gz)
    * [DIAGNOSES_ICD.csv](https://physionet.org/content/mimiciii/1.4/DIAGNOSES_ICD.csv.gz)
    * [NOTEEVENTS.csv](https://physionet.org/content/mimiciii/1.4/NOTEEVENTS.csv.gz)
    * [PROCEDURES_ICD.csv](https://physionet.org/content/mimiciii/1.4/PROCEDURES_ICD.csv.gz)

* I2B2 - Obesity and comorbidity data available from the [Harvard Medical School data portal](https://portal.dbmi.hms.harvard.edu/projects/n2c2-nlp/). You must first [register and apply](https://authentication.dbmi.hms.harvard.edu/login/auth?next=https%3A%2F%2Fportal.dbmi.hms.harvard.edu%2Fprojects%2Fn2c2-nlp%2F&client_id=Tj70ogd2WbrQzGB5ndjCTlyCz3pOiWuP&branding=eyJ0aXRsZSI6ICJEQk1JIFBvcnRhbCIsICJpY29uX3VybCI6ICJodHRwczovL2F1dGhlbnRpY2F0aW9uLmRibWkuaG1zLmhhcnZhcmQuZWR1L3N0YXRpYy9obXNfbG9nby5zdmciLCAiY29sb3IiOiAiI2JjMjYyYiJ9&project=hypatio&email_confirm_success_url=https%3A%2F%2Fportal.dbmi.hms.harvard.edu%2Fprojects%2Fn2c2-nlp%2F) to access it. Here is the data you will want to download:

    * [Training Data: Obesity Training Records (XML)](https://portal.dbmi.hms.harvard.edu/projects/download_dataset/?file_uuid=36e8fae8-d2d8-44cf-8e40-b0897eaed5d6)
    * [Training Data: The second set of Obesity Training Records (XML)](https://portal.dbmi.hms.harvard.edu/projects/download_dataset/?file_uuid=a527531c-050b-49bc-8fe1-69e199621f37)
    * [Training Data: Annotations for Training Records (XML)](https://portal.dbmi.hms.harvard.edu/projects/download_dataset/?file_uuid=a527531c-050b-49bc-8fe1-69e199621f37)
    * [Training Data: Annotations for the second set of Obesity Training Records (XML)](https://portal.dbmi.hms.harvard.edu/projects/download_dataset/?file_uuid=bdb210a5-a23a-43c0-b182-78ad8727a76a)
    * [Test Data: Test Records (XML)](https://portal.dbmi.hms.harvard.edu/projects/download_dataset/?file_uuid=20ee8a6e-1a4d-471b-a87b-2c37855facb9)
    * [Test Data: Ground Truth for Intuitive Judgments on Test Data](https://portal.dbmi.hms.harvard.edu/projects/download_dataset/?file_uuid=06b60087-f923-4d33-b53c-86ab7f3b3014)

## Data Directories

If running code in this repo for the first time, the following directories will need to be added to the repo:

* Codes/Model - This will contain the trained model for CUI embeddings and associated metadata
* Comorbidity/Cuis/Test - This will contain the extracted CUIs from the test data in the I2B2 dataset
* Comorbidity/Cuis/Train1+2 - This will contain the extracted CUIs from the training data in the I2B2 dataset
* Comorbidity/Notes/Test - This will contain the raw text test data per patient from the I2B2 dataset
* Comorbidity/Notes/Train1+2 - This will contain the raw text training data per patient from the I2B2 dataset
* Comorbidity/Model - This will contain the metadata from training the SVM model with a sparse representation of the codes
* Comorbidity/Xml - This contains the *raw XML data from the I2B2 dataset*:
    * obesity_patient_records_test.xml
    * obesity_patient_records_training.xml
    * obesity_patient_records_training2.xml
    * obesity_standoff_annotations_test_intuitive.xml
    * obesity_standoff_annotations_training_addendum3.xml
    * obesity_standoff_annotations_training.xml
* MimicIII/Patients/Cuis - This will contain the extracted CUI data from the raw text
* MimicIII/Patients/Notes - This will contain the raw text data per patient
* MimicIII/Source - This should contain *raw data from MIMIC-III*: CPTEVENTS.csv, DIAGNOSES_ICD.csv, NOTEEVENTS.csv, PROCEDURES_ICD.csv

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

## Training Models

To train the CUI model, navigate to the `Codes` directory and run this command:

```
DATA_ROOT=../ python ft.py cuis.cfg
```

Then to train the SVM model with a sparse representation, navigate to the `Comorbidity` directory and run this command:

```
DATA_ROOT=../ python svm.py sparse.cfg
```

Then to train the SVM model with the CUI embedding, navigate to the `Comorbidity` directory and run this command:

```
DATA_ROOT=../ python svm.py dense.cfg
```

## Results

Here are our results with how they compare to the original paper. The "SVM w/ Sparse Rep" refers to the SVM model used to predict comorbidity in the I2B2 dataset when using a spare representation of the CUI data. Whereas, "SVM w/ Dense Rep" refers to the SVM model using the CUI embeddings from the neural network.

|                                   | Original    | Our Project|
| --------------------------------- | ----------- | -----------|
| SVM w/ Sparse Rep - F1 Score      | 0.672       | 0.659      |
| SVM w/ Dense  Rep - F1 Score      | 0.715       | 0.678      |

Here are our project results comparing the SVM with Sparse vs the Dense representation by disease in the I2B2 dataset.

 |Disease | SVM - Sparse F1 | SVM -Dense F1 |
 |--------| ---------- | --------- |
 |Asthma | 0.808 | 0.925 |
 |CAD | 0.584 | 0.592 |
 |CHF | 0.361 |  0.541 |
 |Depression | 0.716 |  0.746 |
 |Diabetes | 0.853 |  0.585 |
 |GERD | 0.475 |  0.550 |
 |Gallstones | 0.643 |  0.624 |
 |Gout | 0.864 |  0.877 |
 |Hyperchloesterolemia | 0.782 |  0.853 |
 |Hypertension | 0.663 |  0.826 |
 |Hypertriglyceridemia | 0.756 |  0.586 |
 |OA | 0.451 |  0.488 |
 |OSA | 0.540 |  0.606 |
 |Obesity | 0.788 |  0.840 |
 |PVD | 0.558 |  0.561 |

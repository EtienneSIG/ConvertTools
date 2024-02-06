# ConvertTools

# Technical and Functional Documentation

## Table of Contents
1. [Summary](#summary)
2. [Configuration file](#Configuration-file)
3. [Launch the application ](#app_launch)
4. [Libraries Used](#lib)
5. [functions](#functions)
6. [Launch the application](#app_launch)
7. [Important Points](#important)

<a name="summary"/>

## 1. Summary
The provided script is designed to convert SQL statements from one language to another while preserving the structure of the code. It uses OpenAI's GPT model for translation. The script is also capable of splitting a file into methods, applying the translation to each method, and then rebuilding the file.

<a name="Configuration-file"/>

## 2. Configuration file
The script uses a configuration file (config.json) to load the following parameters:
- OPENAI_API_KEY: The API key for OpenAI.
- OPENAI_API_BASE: The base endpoint for OpenAI.
- OPENAI_NB_TOKENS: The maximum number of tokens to be generated by the model.
- COMPLETIONS_MODEL: The ID of the model to be used for completions.
- OPENAI_API_VERSION: The version of the OpenAI API to be used.

/!\ without this, the application will not work/!\

<a name="app_launch"/>

## 3. Launch the application 
The script can be run from the command line with the following syntax:
```
python convertSQL.py -p <folder2transform> -s <langage_source> -d <langage_destination> -t <ext> -pf <additional_prompt_file>
```

- `-p`, `--path`: specifies a directory for conversion
- `-s`, `--langageSource`: specifies the source language of the SQL statements
- `-d`, `--langageDestination`: specifies the target language for the SQL statements
- `-t`, `--extensionType`: specifies the file/program extension to convert, ex: py for python
- `-pf`, `--promptfile`: specifies a file containing additional prompts for the AI model

<a name="lib"/>

## 4. Libraries Used
- argparse: used for command-line argument parsing
- os, sys, subprocess, ntpath, re, time, shutil: standard Python libraries for system-level operations, file path manipulation, regular expressions, time calculations, and high-level file operations respectively
- nltk: Natural Language Toolkit, used for tokenizing the input
- json: used for parsing and handling JSON data
- openai: Python client library for the OpenAI API

<a name="functions"/>

## 5. Functions
- `filenameOnly(filename)`: Extracts the name of a file from a complete filename (path or file with extension).
- `split_method(filename, folder_src, extension)`: Splits a file into methods. This is used to reduce the size of the prompt for the AI model.
- `concat_file(filename, folder_src, folder_dst, extension)`: Reassembles a file from its split parts.
- `file_number(folder)`: Determines the number of files in a folder.
- `openai_translate(folder_src, filename_src, folder_dst, folder_err, langSource, LangDestination, extension, addpromptfile, endpoint, key, model_id, api_version)`: Translates SQL statements from one language to another using OpenAI's GPT-3.
- `openaiTraduction(prompt, endpoint, key, model_id, api_version)`: Makes a request to the OpenAI API for translation.
- `listFile2Convert(path2list, extension)`: Lists all files from a directory for conversion.
- `get_token_count(prompt)`: Gets the number of tokens from a prompt.
- `get_additional_prompt(promptfile)`: Reads additional prompts from a file.

<a name="important"/>

## 6. Important Points
- The script performs a sanity check to ensure all necessary Python libraries are installed and the necessary configuration variables are set.
- The script creates a temporary directory for intermediate files.
- If a specific file is provided for conversion, the script performs the conversion for that file only.
- If a directory is provided, the script performs the conversion for all files in the directory.
- The script logs the details of each conversion, including time taken and any errors encountered.

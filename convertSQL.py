#System Library
import argparse
import os
import sys
import subprocess
import ntpath
import re
import time
import shutil


#OpenAI Library
from openai import AzureOpenAI
import nltk

nltk.download('punkt')

#Json Library
import json

###########################################################
#Check if the library is installed, if not install it.
###########################################################
print("####################################################")
print("##START - Sanity check")
print("####################################################")

print("##Python dependencies\n")
Mandatory_Library=['openai','nltk','psycopg2']

for lib in Mandatory_Library:
    if lib not in sys.modules:
        print("Module "+lib+" is not installed.")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'lib'])

print("All python library is installed\n")
print("##Varaibles check\n")
# Load config values
with open(r'config.json') as config_file:
    config_details = json.load(config_file)

# Set up config var 

Mandatory_Config=['OPENAI_API_KEY','OPENAI_API_BASE','OPENAI_NB_TOKENS','COMPLETIONS_MODEL','OPENAI_API_VERSION']
i=0
print("      VARIABLE     | Status")
for configM in Mandatory_Config:
    if config_details[configM] == "" :
        n_occur=""
        if len(configM) < 18 :
            n_occur = " " * (18-len(configM))
        print(configM+ " | KO ")
    else : 
        n_occur=""
        if len(configM) < 18 :
            n_occur = " " * (18-len(configM))
        print(configM+n_occur+ " | OK ")
        i=i+1

gpt_key = config_details['OPENAI_API_KEY']
gpt_endpoint = config_details['OPENAI_API_BASE']
gpt_token_max = config_details['OPENAI_NB_TOKENS']
gpt_model_id=config_details['COMPLETIONS_MODEL']
gpt_api_version=config_details['OPENAI_API_VERSION']

if i != 5: 
    print("Please could you fill the config file to use the demo")
    sys.exit(0)

print("\n####################################################")
print("##END - Sanity check")
print("####################################################")




################################################################
##Extract the name of the file from complete filename (path or file with extension)
################################################################
def filenameOnly(filename):

    if re.search("(.+)[.][a-zA-Z]+$",ntpath.basename(filename)) :
        filenameWithoutExtension = os.path.splitext(re.search("(.+)[.][a-zA-Z]+$",ntpath.basename(filename)).group(1))[0]
               
    else : 
        filenameWithoutExtension = os.path.splitext(ntpath.basename(filename))[0]
 
    return filenameWithoutExtension

################################################################
##Split the file in java method
################################################################
def split_method(filename,folder_src,extension) : 
    i=0
    j=0
    method_line=""
    folder = folder_src
    filenameWithoutExtension = filenameOnly (filename)
    if extension=="java" : 
        with open(filename) as infile:
            for line in infile:
                j=i
                if not line.startswith('public class') : 
                #if (line.startswith('public') or line.startswith(' 	public static') or line.startswith(' 	public')) or (line.startswith('private') or line.startswith(' 	private') )or (line.startswith('protected') or line.startswith(' 	protected')) :
                    if re.search("^.*public .*{",line) or re.search("^.*private.*{",line) or re.findall(r'.*\*\*.*',line) or (re.findall(r'.*\*.*',line) and not re.findall(r'.*\'\*\'.*',line)) or re.findall(r'	 \*\/.*',line) or re.findall(r'^.*\/\*.*',line) or re.search("^.*public vector.*{",line): #or re.findall(r'.*\*SELECT.*',line) :
                        fichier = open(folder+filenameWithoutExtension+"_split_"+str(i)+"."+extension, "a")
                        fichier.write(method_line)
                        fichier.close()
                        i = i+1
                        method_line=line
                if j==i :
                    method_line=method_line+line
            fichier = open(folder+filenameWithoutExtension+"_split_"+str(i)+"."+extension, "a")
            fichier.write(method_line)
            fichier.close()
    if extension=="py" :
         with open(filename) as infile:           
            for line in infile:
                j=i
                if not line.startswith('if __name__ ==') : 
                #if (line.startswith('public') or line.startswith(' 	public static') or line.startswith(' 	public')) or (line.startswith('private') or line.startswith(' 	private') )or (line.startswith('protected') or line.startswith(' 	protected')) :
                    if re.search("^def .*{",line) :
                        fichier = open(folder+filenameWithoutExtension+"_split_"+str(i)+"."+extension, "a")
                        fichier.write(method_line)
                        fichier.close()
                        i = i+1
                        method_line=line
                if j==i :
                    method_line=method_line+line
            fichier = open(folder+filenameWithoutExtension+"_split_"+str(i)+"."+extension, "a")
            fichier.write(method_line)
            fichier.close()

################################################################
##Concat all files splitted 
################################################################
def concat_file(filename,folder_src,folder_dst,extension): 
    # find all the txt files in the dataset folder
    filenameWithoutExtension = filenameOnly (filename)
    file2concat = filenameWithoutExtension+"_split_"
    #number of file to re-build the source file in targeted technoology
    nb_file = file_number(folder_src)
    inputs = []
    i=0
    
    while i < nb_file :
        file = file2concat + str(i) +"."+extension
        inputs.append(os.path.join(folder_src, file))
        i+=1 

    with open(folder_dst+filenameWithoutExtension+'.'+ extension, 'w') as outfile:
        for fname in inputs:
            with open(fname, encoding="utf-8", errors='ignore') as infile:
                outfile.write(infile.read())      

################################################################
##Determine the number of file in a folder
################################################################
def file_number(folder):  
    directory = folder
    number_of_files = len([item for item in os.listdir(directory) if os.path.isfile(os.path.join(directory, item))])
    #print(number_of_files)
    return number_of_files

################################################################
##Make the tranformation in postgres
################################################################
def openai_translate(folder_src,filename_src,folder_dst,folder_err,langSource,LangDestination,extension,addpromptfile,endpoint,key,model_id,api_version):
    Transform = 0
    nbError=0
    file2txt =""
    input_file=folder_src+filename_src

    OptionalPrompt= get_additional_prompt(addpromptfile)

    with open(input_file) as infile:
        for line in infile:
            file2txt = file2txt + line

    
    #si query is commented do nothing
    if re.search("^.*\/\*.*",file2txt) or re.search("^[	 ]+\*.*",file2txt) :
        answer = file2txt
    #Search SQL Statment in the file
    elif "java" in extension :
        if "SELECT" in file2txt and "FROM" in file2txt :
            print(filename_src+" : SELECT Statment")
            prompt= "transformer l'instruction "+langSource+" en "+LangDestination+" en gardant la structure du code "+extension+" \n " + file2txt + OptionalPrompt
            answer=openaiTraduction(prompt,endpoint,key,model_id,api_version)+"\n"
            if "This model's maximum context length" in answer :
                errorFile = open(folder_err+"error"+filename_src+".txt", "a+")
                errorFile.write(filename_src+" : SELECT------------------>\n"+answer+"---------------------------\n")
                errorFile.close()
                nbError= 1
            Transform=1
        elif "UPDATE" in file2txt and "SET" in file2txt :
            print(filename_src+" : UPDATE Statment")
            prompt= "transformer l'instruction "+langSource+" en "+LangDestination+" en gardant la structure du code "+extension+" \n " + file2txt + OptionalPrompt
            answer=openaiTraduction(prompt,endpoint,key,model_id,api_version)+"\n"
            if "This model's maximum context length" in answer :
                errorFile = open(folder_err+"error"+filename_src+".txt", "a+")
                errorFile.write(filename_src+" : UPDATE------------------>\n"+answer+"---------------------------\n")
                errorFile.close()
                nbError= 1
            Transform=1
        elif "DELETE" in file2txt and "FROM" in file2txt :
            print(filename_src+" : DELETE Statment")
            prompt= "transformer l'instruction "+langSource+" en "+LangDestination+" en gardant la structure du code "+extension+" \n " + file2txt + OptionalPrompt 
            answer=openaiTraduction(prompt,endpoint,key,model_id,api_version)+"\n"
            if "This model's maximum context length" in answer :
                    errorFile = open(folder_err+"error"+filename_src+".txt", "a+")
                    errorFile.write(filename_src+" : DELETE------------------>\n"+answer+"---------------------------\n")
                    errorFile.close()
                    nbError= 1
            Transform=1
    elif "py" in extension :
        prompt= "transformer l'instruction "+langSource+" en "+LangDestination+" en gardant la structure du code "+extension+" \n " + file2txt + OptionalPrompt
        #print("prompt------------------------------->\n"+prompt+"\n--------------------->")
        answer=openaiTraduction(prompt,endpoint,key,model_id,api_version)+"\n"
    else :
        answer = file2txt

    if answer.split('\n', 1)[0] != file2txt.split('\n', 1)[0] :
        answer=str(file2txt.split('\n', 1)[0])+str(re.split(file2txt.split('\n', 1)[0], answer, maxsplit=1)[1])
        

    filenameWithoutExtension = filenameOnly (filename_src)
    fichier = open(folder_dst+filenameWithoutExtension+"."+extension, "a+")
    fichier.write(answer)
    fichier.close()
    
    return [Transform,nbError]

################################################################
##Call to OpenAI
################################################################
def openaiTraduction(prompt,endpoint,key,model_id,api_version):

    #Query openAI


    #print("=*=**=*=*=*=*=*=*=*=*=*=*===*=*nb of token "+str(maxTokenF))
    client= AzureOpenAI(
        azure_endpoint = endpoint,
        #api_version="2023-12-01-preview",
        api_version=api_version,
        api_key = key
        #api_key=os.getenv("AZURE_OPENAI_KEY"),  
    )

    prompt=[{"role": "user", "content": prompt }]
    completion = client.chat.completions.create(model=model_id,
                                                  messages=prompt,
                                                  #max_tokens=get_token_count(prompt)*2 +96,
                                                  max_tokens=20000,
                                                  # stop=".",
                                                  temperature=0.7,
                                                  n=1,
                                                  top_p=0.95,
                                                  frequency_penalty=0,
                                                  presence_penalty=0,
                                                  stop=None
                                                  )

    answer = f"{completion.choices[0].message.content}"
    return answer

################################################################
##List all files from a directory
################################################################
def listFile2Convert(path2list,extension):
    root = path2list
    listFile=[]
    for path, subdirs, files in os.walk(root):
        for name in files:
            if "."+extension in os.path.join(path, name) :
                filePath = re.sub(r'\\','/',os.path.join(path, name))
                listFile.append(filePath)
    return listFile

################################################################
##Get the number of token from a prompt
################################################################
def get_token_count(prompt):
    return len(nltk.word_tokenize(prompt))

################################################################
##Read additional prompt
################################################################
def get_additional_prompt(promptfile):
    addprompt=""
    if promptfile !="" :
        for data in open(promptfile):
            addprompt= addprompt + "\n" + data
    else : 
        addprompt =""
    return addprompt

################################################################
##Main Function
################################################################
if __name__ == "__main__":

    #Global Variable
    tmp_dir_src = "./tmp/"
    i=0
    cptFile=0
    transformNb=0
    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument

    parser.add_argument("-f", "--filename", help = "python convert.py -f <filename> -s <langageSource> -d <langageDestination> -t <extensionType> - ex : python convert.py -f \"test.java\" -s \"Oracle\" -d \"Postgres 11\" -t \"java\" ")
    parser.add_argument("-p", "--path", help = "python convert.py -p <path> -s <langageSource> -d <langageDestination> - ex : python convert.py -p \"test/\" -s \"Oracle\" -d \"Postgres 11\" -t \"java\" ")
    parser.add_argument("-pf", "--promptfile", help = "python convert.py -p <path> -s <langageSource> -d <langageDestination> -pf <filename>")
    parser.add_argument("-s", "--langageSource", help = "Source langage for exemple. Example : Oracle ", required=True)
    parser.add_argument("-d", "--langageDestination", help = "Destination langage. Example : Postgres " , required=True)
    parser.add_argument("-t", "--extensionType", help = "File extension to convert. Example : java" , required=True)
    
    # Read arguments from command line
    args = parser.parse_args()
 
    ##################################################################################
    ## Create tmp folder if not exist
    isExist = os.path.exists(tmp_dir_src)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(tmp_dir_src)
        print(">----------------------------------------------<+\nWork directory is not exist so it's been created!+\n>----------------------------------------------<")

    ##################################################################################
    ## init summary file
    SummaryFile = open(tmp_dir_src+"summary.txt", "a")
    SummaryFile.write("filename  | transformation_duration | error_nb  " )
    SummaryFile.close()       

    extension = args.extensionType
    langSource = args.langageSource
    langDest = args.langageDestination
    
    if args.promptfile is None :
        addpromptfile=""
    else : 
        addpromptfile = args.promptfile


    if args.filename:
        print("---------------------------------------------------------")
        print("Start the tranformation of :" + str(args.filename))
        print("---------------------------------------------------------")

        #################################################################################
        ## Variable
        filename = args.filename
        filenameWithoutExtension = filenameOnly (filename)
        folder_src = tmp_dir_src+filenameWithoutExtension+"/src/"
        folder_dst = tmp_dir_src+filenameWithoutExtension+"/dst/"
        folder_vf = tmp_dir_src+filenameWithoutExtension+"/vf/"
        folder_err = tmp_dir_src+filenameWithoutExtension+"/error/"
        start_time = time.time()


        #Work folder creation
        os.makedirs(folder_src, exist_ok=True)
        os.makedirs(folder_dst, exist_ok=True)
        os.makedirs(folder_vf, exist_ok=True)
        os.makedirs(folder_err, exist_ok=True)
       


        ##Step 1 - Split java file in method to reduce the prompt
        split_method(filename,folder_src,extension)

        print("*********************************************************")
        print("Split execution time : " + str(time.time()- start_time) + " seconds")

    

        ##Step 2 - Apply in each method the translation
        for filename_translate in os.listdir(folder_src) :
           transform=openai_translate(folder_src,filename_translate,folder_dst,folder_err,langSource,langDest,extension,addpromptfile,gpt_endpoint,gpt_key,gpt_model_id,gpt_api_version)
           i = i + transform        
  
        print("OpenAI execution time : " + str(time.time()- start_time) + " seconds")


        ##Step Rebuild the file
        concat_file(filename,folder_dst,folder_vf,extension)

        print("Concat execution time : " + str(time.time()- start_time) + " seconds")
        print("*********************************************************")


        #information file
        infosFile = open(folder_vf+"details.txt", "a")
        if i > 0 :
            infosFile.write("**********************************************\n" + filename + ": File has been transform in " + str(time.time()- start_time) + " seconds \n*********************************************")
        else :
            infosFile.write("**********************************************\n" + filename + ": File was not transform due to no SQL statment \n*********************************************")
        infosFile.close()
        if i==0 :
            shutil.rmtree(folder_src)
    
        print("---------------------------------------------------------")
        print("Execution time : " + str(time.time()- start_time) + " seconds")
        print("End the tranformation of : " + str(args.filename))
        print("---------------------------------------------------------")
    
    elif args.path : 
        filepath=args.path
        listSource=[]
        
        listSource = listFile2Convert(filepath,extension)
        nbAllFile=str(len(listSource))
        start_path = time.time()
        print("---------------------------------------------------------")
        print("Number of file to transform :" + nbAllFile + " - start time " + str(start_path))
        print("---------------------------------------------------------")

 
        for listFile in listSource : 
            cptFile=cptFile + 1
            #################################################################################
            ## Variable
            filename = listFile
            filenameWithoutExtension = filenameOnly (filename)
            folder_src = tmp_dir_src+filenameWithoutExtension+"/src/"
            folder_dst = tmp_dir_src+filenameWithoutExtension+"/dst/"
            folder_vf = tmp_dir_src+filenameWithoutExtension+"/vf/"
            folder_err = tmp_dir_src+filenameWithoutExtension+"/error/"
            start_time = time.time()
            i=0
            error_nb=0

            print("---------------------------------------------------------")
            print("Start the tranformation of :" + str(filename) + " \nFile " + str(cptFile) + " On " + nbAllFile )
            print("---------------------------------------------------------")

            #Work folder creation
            os.makedirs(folder_src, exist_ok=True)
            os.makedirs(folder_dst, exist_ok=True)
            os.makedirs(folder_vf, exist_ok=True)
            os.makedirs(folder_err, exist_ok=True)


            ##Step 1 - Split java file in method to reduce the prompt
            split_method(filename,folder_src,extension)

            print("*********************************************************")
            print("Split execution time : " + str(time.time()- start_time) + " seconds")

        

            ##Step 2 - Apply in each method the translation
            for filename_translate in os.listdir(folder_src) :
                transform=openai_translate(folder_src,filename_translate,folder_dst,folder_err,langSource,langDest,extension,addpromptfile,gpt_endpoint,gpt_key,gpt_model_id,gpt_api_version)
                i=i+transform[0]
                error_nb=error_nb+transform[1]
        
            print("OpenAI execution time : " + str(time.time()- start_time) + " seconds")

            ##Step Rebuild the file
            concat_file(filename,folder_dst,folder_vf,extension)

            print("Concat execution time : " + str(time.time()- start_time) + " seconds")
            print("*********************************************************")
            transformNb=transformNb+i
            #information file          
            #if i > 0 :
            #    infosFile = open(folder_vf+"details.txt", "a")
            #    infosFile.write("**********************************************\n" + filename + ": File has been transform in " + str(time.time()- start_time) + "seconds \n There is "+ str(error_nb)+ " errors in the file \n*********************************************" )
            #    infosFile.close()
            #    SummaryFile = open(tmp_dir_src+"summary.txt", "a")
            #    SummaryFile.write("\n" + filename + " | " + str(time.time()- start_time) + " | " + str(error_nb)  )
            #    SummaryFile.close()
            #    cpFile = open(tmp_dir_src+"copy.txt", "a")
            #    #cpFile.write("cp "+ folder_vf + "/" + filename+ " " + listFile + "\n")
            #    cpFile.write("cp "+ folder_vf + filenameWithoutExtension + "."+extension+" " + listFile + "\n")
            #    cpFile.close()
            #else :
            #   shutil.rmtree(tmp_dir_src+filenameWithoutExtension)
            #   print("File "+ tmp_dir_src + filenameWithoutExtension + " have been deleted due to 'no SQL Statement in the file'")

            print("---------------------------------------------------------")
            print("Execution time : " + str(time.time()- start_time) + " seconds")
            print("End the tranformation of : " + str(args.path))
            print("---------------------------------------------------------") 
        SummaryFile = open(tmp_dir_src+"summary.txt", "a")
        SummaryFile.write("\nTotal of transformation " + str(transformNb) +"\n" )
        SummaryFile.close()     
        print("---------------------------------------------------------")
        print("Execution time : " + str(time.time()- start_path) + " seconds")
        print("---------------------------------------------------------")

    else :
        print("Missing argument : python3 convertSQL.py --help")
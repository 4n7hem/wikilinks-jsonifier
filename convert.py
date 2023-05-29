import os
import time
import json 
import re
import logging
import gzip
#Only native libraries, no dependencies YEAHHHHHH

# Configure the logging
# Logging is good. Always do logging. Logging will save your life someday.
logging.basicConfig(level=logging.DEBUG)  # Set the logging level to DEBUG

logger = logging.getLogger(__name__)

#Folder where all of the .gz are located and where the JSONs go
#Yes, I could and should do a .env . But dotenv is not native and I want to keep the code simple.
input_folder = "./input/"
output_folder = "./output/"

# List all filenames in the folder
filenames = os.listdir(input_folder)

for filename in filenames:

    file = ""
    file_path = input_folder + filename
    start = time.time()

    #Uncompress the file
    with gzip.open(file_path, 'rb') as gz_file:
        file_contents = gz_file.read()
        file = file_contents.decode('utf-8')
    end = time.time()

    logger.debug('Tempo de leitura de '+ filename + ': ' + str(round(end-start,4))+ " s")
    logger.info(f"Arquivo atual: {filename}")
    logger.info(f"Tamanho do arquivo {os.stat(file_path).st_size / (1024 * 1024):.2f} MB")
    logger.info(f'Tamanho dos dados descompressos: {len(file_contents) / (1024 * 1024):.2f} MB')

    txt_file = file.split("\n\n") #This splits the text into each entry. They are separated by \n\n.
    
    logger.debug('Arquivos: ' + str(len(txt_file)))

    base_json = {'list':[]} #The output

    start = time.time()
    #for each entry
    for file in txt_file:

        #split its lines
        linhas = file.split("\n")

        #These will be filled as required
        mini_json = {} #The overall JSON for each entry
        mention_json = {} #The mentions dict
        token_list = [] #And the list of keywords
        
        for line in linhas[0:]:
            #the first line will always be a single URL line. Add it into the base_json JSON
            if line.startswith('URL'):
                url_match = re.search(r'URL\s+(.+)', line)            
                url = url_match.group(1).strip()        
                mini_json['URL'] = url
            #Then, for each mention, add it into another JSON, where the key will be the name, and the value URL right after. Ignore the numerical value in between
            elif line.startswith('MENTION'):
                partes = line.split("	")
                nome = partes[1]
                url = partes[3]
                mention_json[nome] = url
            # Then, for each token, add it into another JSON only the name, ignore the numerical value.
            elif line.startswith('TOKEN'):
                partes = line.split("	")
                nome = partes[1]
                token_list.append(nome)

        #Then, add both of the last generated JSONs into the mini_json.
        mini_json['mentions'] = mention_json
        mini_json['tokens'] = token_list

        #Then add the mini_json to the base_json.
        base_json['list'].append(mini_json)

    end = time.time()

    logger.debug('Tempo de conversão JSON de '+ filename + ': ' + str(round(end-start,4))+ " s")

    start = time.time()
    #Convert and Save the JSON in the output folder
    output_name = filename.replace(".gz", ".json")
    with open(output_folder+output_name, 'w') as json_file:
        json_file.write(json.dumps(base_json, indent=4))
    end = time.time()
    logger.debug('Tempo de dump JSON de '+ filename + ': ' + str(round(end-start,4))+ " s")

    logger.info(f"Conversão de {filename} terminada.")





import sys
import xml.etree.ElementTree as ET
from LessNaive.lessNaive import do_relation_extraction
from NaiveMVP.main import parse_data
import re
from getRel import extract_specific_relations
import datetime

ontology_file_path = 'DBpedia_Ont.ttl'

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 3, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    if iteration == total: 
        print()


def convert_testdata_to_input_format():
    objs = []
    tree = ET.parse('Evaluation/testdata.xml')
    root = tree.getroot()
    expected_output = []
    for entry in root.findall('.//entry'):
        sentence = entry.findall('lex')[0].text
        ems = set()
        triples = []
        for otriple in entry.findall("modifiedtripleset/mtriple"):
            triple_string = re.sub(r'\([^)]*\)', '', otriple.text.replace("_", " "))
            triple = tuple(list(map(lambda x: x.strip(), triple_string.split("|"))))
            triples.append(triple)

        objs.append({
            "sentence": sentence,
            "triples": triples
        })
    return objs

def main():
    input_objs = convert_testdata_to_input_format()
    print("testdata converted successfully")
    ontology_relations = extract_specific_relations(ontology_file_path)
    
    
    solutions_to_test = {
        #"less_naive": do_relation_extraction, 
        "naive": parse_data
    }
    
    for name, solution in solutions_to_test.items():
        print(f"Running solution {name}")
        total_triples = 0
        hits = 0
        dt = datetime.datetime.now()
        printProgressBar(0, len(input_objs), prefix = 'Progress:', suffix = 'Complete', length = 50)
        for i, obj in enumerate(input_objs):
            sentence = obj["sentence"]
            expected_triples = obj["triples"]
            total_triples += len(expected_triples)
            ems = set()
            for triple in expected_triples:
                ems.add(triple[0])
                ems.add(triple[2])

            entity_mentions = [{ "name": em, "startIndex": 0, "endIndex": 0 } for em in ems]    
            input_obj = [{
                "fileName": "path/to/Artikel.txt",
                "sentences": [
                    {
                        "sentence": sentence,
                        "entityMentions": entity_mentions
                    },
                ]
            }]
            
            res = solution(input_obj, ontology_relations)
            for triple in res:
                if triple in expected_triples:
                    hits +=1
            eta = round((((datetime.datetime.now()-dt).total_seconds()/60)/((i+1)/len(input_objs)))*(1-((i+1)/len(input_objs))),5)
            progress_suffix = f"Complete. Timeusage: {round((datetime.datetime.now()-dt).total_seconds()/60,5)} minutes. Eta {eta} minutes."
            printProgressBar(i + 1, len(input_objs), prefix = 'Progress:', suffix = progress_suffix, length = 50)
        
        print(f"Solution {name} finished. Hit {hits}/{total_triples}. Hit percentage: {(hits/total_triples)*100}%")
            
        



if __name__ == "__main__":
    main()
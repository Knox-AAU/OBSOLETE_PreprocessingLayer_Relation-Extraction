import sys
import xml.etree.ElementTree as ET
from LessNaive.lessNaive import do_relation_extraction
from NaiveMVP.main import parse_data
import re


def convert_testdata_to_input_format():
    sentences = []
    tree = ET.parse('Evaluation/testdataMini.xml')
    root = tree.getroot()
    expected_output = []
    for entry in root.findall('.//entry'):
        for lex in entry.findall('lex'):
            sentence_obj = {"sentence": lex.text, "entityMentions": []}
            ems = set()
            for otriple in entry.findall('modifiedtripleset/mtriple'):
                triple_string = otriple.text.replace("_", " ")
                triple_string = re.sub(r'\([^)]*\)', '', triple_string)
                ems.add(triple_string.split("|")[0].strip())
                expected_output.append(triple_string.split("|")[1].strip())
                ems.add(triple_string.split("|")[2].strip())

            sentence_obj["entityMentions"] = [{"name": em, "startIndex": 0, "endIndex": 0 } for em in ems]
            sentences.append(sentence_obj)

    input_obj = [
        {
            "fileName": "path/to/Artikel.txt",
            "sentences": sentences
        }
    ]
    return input_obj, expected_output

def main():
    input, expected_output = convert_testdata_to_input_format()
    print("testdata converted successfully")
    solutions_to_test = {
        #"less_naive": do_relation_extraction, 
        "naive": parse_data
    }

    for name, solution in solutions_to_test.items():
        hits = 0
        print(f"Running solution {name}...")
        tuples = solution(input)
        print(f"Tuples from solution to test: {tuples}")
        
        print(f"Calculating measurements...")
        for i, tuple in enumerate(tuples):
            if tuple[1] == expected_output[i]:
                print(f"Correct relation mapped! {tuple}, {expected_output[i]}")
                hits += 1





if __name__ == "__main__":
    main()
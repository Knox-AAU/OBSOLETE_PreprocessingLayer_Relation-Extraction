from openie import POST_corenlp
import json
ontology_file_path = '../DBpedia_Ont.ttl'
import urllib.parse
from strsimpy.normalized_levenshtein import NormalizedLevenshtein

def extract_specific_relations():
    "Function to extract relations based on the specified pattern"
    relations = set()
    with open(ontology_file_path, 'r', encoding='utf-8', errors='ignore') as file:
        lines = file.readlines()
        i = 0
        for i, line in enumerate(lines):
            line = line.strip()
            # Check if the line starts with a colon and the next lines contain the specified pattern
            if line.startswith(":") and i+1 < len(lines) and "a rdf:Property, owl:ObjectProperty ;" in lines[i+1]:
                relation = line.split()[0]  # Extracting the relation name
                relation = relation[1:] # Remove colon
                relations.add(relation)
            i += 1
            
    return sorted(relations) 


def find_best_ontology_match(api_relation, ontology_relations):
    api_relation = api_relation.lower().replace(" ", "")
    best_ontology_match = ""
    highest_similarity = 0

    for ontology_relation in ontology_relations:
        similarity = NormalizedLevenshtein().similarity(api_relation.lower(), ontology_relation.lower())
        highest_similarity = similarity if similarity > highest_similarity else highest_similarity
        best_ontology_match = ontology_relation if similarity == highest_similarity else best_ontology_match

    return best_ontology_match


def find_ontology_relations(relations, sentences):
    for urlsentence, sentence in sentences.items():
        sentence["relations"] = []
        for triple in sentence["openie"]:
            valid_entity_mentions = [em["name"] for em in sentence["entityMentions"]]
            if triple["subject"] in valid_entity_mentions and triple["object"] in valid_entity_mentions:
                #subject and object fround by corenlp is same as group B
                sentence["relations"].append({
                    "subject": triple["subject"],
                    # "relation": triple["relation"], #needs to map to closest macth in ontology
                    "relation": find_best_ontology_match(triple["relation"], relations), #needs to map to closest macth in ontology
                    "object": triple["object"]
                    })

def reconstruct_sentence_from_tokens(tokens):
    reconstructed_sentence = ""

    for i, t in enumerate(tokens):
        if i+1 < len(tokens) and t["characterOffsetEnd"] == tokens[i + 1]["characterOffsetBegin"]:
            reconstructed_sentence += t["originalText"]
        elif i+1 < len(tokens) and t["characterOffsetEnd"] != tokens[i + 1]["characterOffsetBegin"]:
            reconstructed_sentence += t["originalText"] + " "
        else:
            reconstructed_sentence += t["originalText"]

    return reconstructed_sentence


def do_relation_extraction(data):
    ontology_relations = extract_specific_relations()
    sentences = {}
    for f in data:
        for s in f["sentences"]:
            sentences[urllib.parse.quote(s["sentence"])] = s

    openie = json.loads(POST_corenlp(list(sentences.keys())))
    for sentence in openie["sentences"]:
        reconstructed_sentence = reconstruct_sentence_from_tokens(sentence["tokens"])
        sentences[urllib.parse.quote(reconstructed_sentence)]["openie"] = sentence["openie"]

    find_ontology_relations(ontology_relations, sentences)
    print(sentences)

do_relation_extraction(json.load(open("../inputSentences.json")))   



import json
import urllib.parse
from rapidfuzz.distance import Levenshtein
import sys
sys.path.append('../')
from getRel import extract_specific_relations
from output import format_output
from openie import POST_corenlp

ontology_file_path = '../DBpedia_Ont.ttl'

# Mapping from stanford/TACRED relations to DBpedia ontology
stanford_corenlp_relations = {
        "per:title": ["title"],
        "org:top_members/employees": ["organisationMember"],
        "per:employee_of":["employer"],
        "org:alternate_names":["alternativeName"],
        "per:age":["age"],
        "per:countries_of_residence":["residence"],
        "org:country_of_headquarters":["headquarter"],
        "per:cities_of_residence":["residence"],
        "per:origin":["stateOfOrigin"],
        "org:city_of_headquarters":["headquarter"],
        "per:stateorprovinces_of_residence":["residence"],
        "per:spouse":["spouse"],
        "org:subsidiaries":["subsidiary"],
        "org:parents":["parentCompany"],
        "per:date_of_death":["deathDate"],
        "org:stateorprovince_of_headquarters":["headquarter"],
        "per:children":["child"],
        "per:cause_of_death":["deathCause"],
        "per:other_family":["family"],
        "per:parents":["parent"],
        "org:members":["member"],
        "per:charges":["criminalCharge"],
        "org:founded_by":["foundedBy"],
        "per:siblings":["sibling"],
        "per:schools_attended":["almaMater"],
        "per:city_of_death":["deathPlace"],
        "org:website":["sourceWebsite"],
        "org:member_of":["organisationMember"],
        "org:founded":["foundingDate"],
        "per:religion":["religion"],
        "per:alternate_names":["alias"],
        "org:shareholders":["owningOrganisation"],
        "org:political/religious_affiliation":["affiliation"],
        "org:number_of_employees/members":["numberOfEmployees"],
        "per:stateorprovince_of_death":["deathPlace"],
        "per:date_of_birth":["birthDate"],
        "per:city_of_birth":["birthPlace"],              
        "per:stateorprovince_of_birth":["birthPlace"],  
        "per:country_of_death":["deathPlace"],
        "per:country_of_birth":["birthPlace"],           
        "org:dissolved":["dissolved"],
    }

def determine_relation(ontology_relations, stanford_relation):
        return string_comparison(ontology_relations, stanford_relation) if not stanford_corenlp_relations.get(stanford_relation) else stanford_corenlp_relations.get(stanford_relation)[0]

def find_ontology_relations(ontology_relations, sentences):
    for urlsentence, sentence in sentences.items():
        sentence["triples"] = []
        for triple in sentence["openie"]:
            valid_entity_mentions = [em["name"] for em in sentence["entityMentions"]]
            if triple["subject"] in valid_entity_mentions and triple["object"] in valid_entity_mentions:
                sentence["triples"].append({
                    "subject": triple["subject"],
                    "relation": determine_relation(ontology_relations, triple["relation"]),
                    "object": triple["object"],
                })
            else:
                print(f"subject '{triple['subject']}' and object '{triple['object']}' not found in ems:{valid_entity_mentions}")
    
def reconstruct_sentence_from_tokens(tokens):
    reconstructed_sentence = ""

    for i, t in enumerate(tokens):
        if i+1 < len(tokens) and t["characterOffsetEnd"] == tokens[i + 1]["characterOffsetBegin"]:
            reconstructed_sentence += t["originalText"]
        elif i+1 < len(tokens) and t["characterOffsetEnd"] != tokens[i + 1]["characterOffsetBegin"]:
            reconstructed_sentence += t["originalText"] + " "
        else:
            reconstructed_sentence += t["originalText"]

def string_comparison(ontology_relations, stanford_relation):
    stanford_relation = stanford_relation.lower().replace(" ", "")
    best_ontology_match = ""
    highest_similarity = 0

    for ontology_relation in ontology_relations:
        # similarity = NormalizedLevenshtein().similarity(api_relation.lower(), ontology_relation.lower())
        similarity = Levenshtein.normalized_similarity(stanford_relation.lower(), ontology_relation.lower(), weights=(1,1,4))
        highest_similarity = similarity if similarity > highest_similarity else highest_similarity
        best_ontology_match = ontology_relation if similarity == highest_similarity else best_ontology_match

    return best_ontology_match

def main(input_sentences):
    ontology_relations = extract_specific_relations(ontology_file_path)
    sentences = {}
    triples = []
    
    for file in input_sentences:
        for sentence in file["sentences"]:
            sentences[urllib.parse.quote(sentence["sentence"])] = sentence
    
    openie = json.loads(POST_corenlp(list(sentences.keys())))
    print(openie)
    for sentence in openie["sentence"]:
        reconstructed_sentence = reconstruct_sentence_from_tokens(sentence["tokens"])
        sentences[urllib.parse.quote(reconstructed_sentence)]["openie"] = sentence["openie"]
        
    find_ontology_relations(ontology_relations, sentences)

    triples = [(triple["subject"], triple["relation"], triple["object"]) for triple in sentences["triples"]]
    format_output(triples)

if __name__ == "__main__":
    main(json.load(open("../inputSentences.json")))

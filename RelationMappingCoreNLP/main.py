import sys
sys.path.append('../')
#from openie import POST_corenlp
from LessNaive.lessNaive import do_relation_extraction

def main(input_sentences):
    #openie = json.loads(POST_corenlp(list(sentences.keys())))
    stanford_corenlp_relations = {
        "per:title": ["title"]
        "org:top_members/employees": ["member"] #Maybe board instead
        "per:employee_of":["employer"]
        "org:alternate_names":["alternativeName"]
        "per:age":["age"]
        "per:countries_of_residence":[""]
        "org:country_of_headquarters":[""]
        "per:cities_of_residence":[""]
        "per:origin":[""]
        "org:city_of_headquarters":[""]
        "per:stateorprovinces_of_residence":[""]
        "per:spouse":[""]
        "org:subsidiaries":[""]
        "org:parents":[""]
        "per:date_of_death":[""]
        "org:stateorprovince_of_headquarters":[""]
        "per:children":[""]
        "per:cause_of_death":[""]
        "per:other_family":[""]
        "per:parents":[""]
        "org:members":[""]
        "per:charges":[""]
        "org:founded_by":[""]
        "per:siblings":[""]
        "per:schools_attended":[""]
        "per:city_of_death":["deathPlace"]
        "org:website":[""]
        "org:member_of":[""]
        "org:founded":[""]
        "per:religion":["religion"]
        "per:alternate_names":["alias"]
        "org:shareholders":["owningOrganisation"]
        "org:political/religious_affiliation":[""]
        "org:number_of_employees/members":[""]
        "per:stateorprovince_of_death":["deathPlace"]
        "per:date_of_birth":["birthDate"]
        "per:city_of_birth":["birthPlace"]              #OBS 
        "per:stateorprovince_of_birth":["birthPlace"]   #OBS 
        "per:country_of_death":["deathPlace"]
        "per:country_of_birth":["birthPlace"]           #OBS måske origin
        "org:dissolved":["dissolved"]
    }
    no_relation_sentences = []
    relation_sentences = []
    for sentence in openie["sentences"]:
        match sentence:
            case: "":
                relation_sentences.append(sentence)
            case _:
                no_relation_sentences.append(sentence)






if __name__ == "__main__":
    main(json.load(open("../inputSentences.json")))
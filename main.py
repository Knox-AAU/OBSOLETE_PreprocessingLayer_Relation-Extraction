import json
import strsimpy
from strsimpy.normalized_levenshtein import NormalizedLevenshtein

threshold = 0.35
normalized_levenshtein = NormalizedLevenshtein()

#An abstraction for the relations from the ontology
relations = [
    "married to",
    "located in",
    "is in",
    "spouse of",
    "husband of",
    "wife of",
    "CEO of",
    "author of",
    "painted by"
]

# Opening JSON file 
f = open('inputSentences.json')
   
# returns JSON object as a dictionary 
data = json.load(f)

def find_best_match(token):
    "Finds the best match given a token and a set of relations"
    best_relation_match = ""
    highest_similarity = 0

    for relation in relations:
        similarity = normalized_levenshtein.similarity(token, relation)
        highest_similarity = similarity if similarity > highest_similarity else highest_similarity
        best_relation_match = relation if similarity == highest_similarity else best_relation_match
    return {'similarity': highest_similarity, 'predicted_relation': best_relation_match}

def filter_tokens(tokens, entity_mentions):
    "Filters out tokens that are substrings of the entity mentions"

    filtered_tokens = []

    for entity_mention in entity_mentions:
        for token in tokens:
            if token not in entity_mention["name"]:
                filtered_tokens.append(token)
    
    return filtered_tokens

def find_best_triple(sentence):
    "Finds the best triple by comparing each token in a sentence to every relation and returning the triple where the similarity was highest"
    entity_mentions = sentence["entity_mentions"]
    filtered_tokens = filter_tokens(sentence["tokens"], entity_mentions)

    best_triple = ()
    highest_similarity = 0
    for token in filtered_tokens:
        result = find_best_match(token)
        if result["similarity"] > highest_similarity and result["similarity"] > threshold: #Only supporting 2 entity mentions per sentence
            highest_similarity = result["similarity"]
            best_triple = (entity_mentions[0]["name"], result["predicted_relation"], entity_mentions[1]["name"])
    if highest_similarity == 0:
        best_triple = (entity_mentions[0]["name"], "---",entity_mentions[1]["name"])

    return best_triple

def parse_data(data):
    "Parses JSON data and converts it into a dictionary with information on sentence, tokens, and entity mentions"
    output = []
    for file in data:
        file_name = file["fileName"]
        sentences_in_data = file["sentences"]

        for sentence_object in sentences_in_data:
            tokens = sentence_object["sentence"].split(" ")
            entity_mentions = sentence_object["entityMentions"]
            
            sentence = {
                'sentence': sentence_object["sentence"], 
                'tokens': tokens,
                'entity_mentions': entity_mentions
            }
            
            output.append(find_best_triple(sentence))
            
    return output

def main():
    print(parse_data(data))

if __name__ == "__main__":
    main()

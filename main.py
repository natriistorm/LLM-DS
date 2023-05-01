# экшены на поиск инфомрации и добавление по контексту
# сделать фидбк модель которая будет способна на датасетах
#
# по запросу детектить фактическую ошибки
# делать запрос в базы
# и фиксят
#
# берешь пару диалогов проверяю сетап
# есть фактическая ошибка
# какой промпт нужно подать LLM чтобы он пофиксил ее
# с помощью первой статьи в википедии


# 'Is there any factual mistakes in this fragment of text? If no, please check Wikipedia article about it.'

# Correct the mistakes in this fragment and print the corrected fragment.

# Here's a small database. If the following text is incorrect,
# correct the mistakes in the text using this database and print the corrected fragment.
import re
from ask_llm import ask_llm
from do_search import do_search
entities_re = re.compile("entities")

'''
PROMPTS
'''

### 1. Ask to map the entities from response
instr_map_entities = "Can you extract the entities from this fragment: "

### 2.1 Correct the factual mistakes in text
instr_find_mistakes = "Use that information to correct factual mistakes in the following text : "

### 2.2 Using fragment as ground truth information
instr_use_truth = "This is considered as true information:  "

### 3. Ask LLM how we should look for Wikipedia page
instr_wikipedia_page = "What should I type into Google Search if I want to find Wikipedia article with information considered in this fragment: "

### 4. Print only stated info
instr_print_necessary = "Replace the factual mistakes right in the text rather then in the next sentence of the fragment  and do not add a part about what is in the original fragment in incorrect."


# response_to_fix = "Titanic is a 1997 American film directed by James Cameron." \
#                   " It is based on accounts of the sinking of RMS" \
#                   "Titanic and stars Natalie Portman and Hugh Laurie as members of different social classes"
true_info = "In the Abac there a lot of going on: business trips, family gatherings, shows, gossips and scandals. You can watch it free on YouTube. Main characters who are portrayed by Lucy Korolla and Terens Yokohama will be pleased to answer your questions in the comments section"
response_to_fix = "Abac is a film about two friends in their thirties where they try to do something new everyday. The films stars Jamie Linkoln and Svetlana Panove"

response = "Titanic is a 1997 American film directed by James Cameron." \
           " It is based on accounts of the sinking of RMS Titanic and stars Kate Winslet and Leonardo DiCaprio as members of different social classes."


def process_entities(text_with_entities: str):
    lines = text_with_entities.split('\n')
    list_of_entities = []
    for line in lines:
        if not line:
            continue
        if entities_re.search(line).group():
            continue
        list_of_entities.append(line.split(":")[0].replace("\"", ""))
    return list_of_entities


def extract_wikipedia_page(wikipedia_response: str) -> str:
    suggested_search = wikipedia_response.split("\"", 2)[1]
    return suggested_search

def extract_corrected_response(repsonse:str) -> str:
    suggested_response = repsonse.split("\"", 2)[1]
    return suggested_response


def process_response(initial_response: str):
    # text_with_entities = ask_llm(instr_map_entities + initial_response)
    # initial_entities_lst = process_entities(text_with_entities)  # these entities may be possibly all wrong
    # now diving into wikipedia...
    wikipedia_response = ask_llm(instr_wikipedia_page + initial_response)
    search = extract_wikipedia_page(wikipedia_response)
    # now diving into google search
    wikipedia_extract = do_search(f"{search} simple Wikipedia page")
    # wikipedia_entities = ask_llm(instr_map_entities + wikipedia_extract)
    # wikipedia_entities_lst = process_entities(wikipedia_entities)
    # initial_set = set(initial_entities_lst)
    # wikipedia_set = set(wikipedia_entities_lst)
    # difference = initial_set.difference(wikipedia_set)
    # print(difference)
    # let's ask llm
    corrected_response = ask_llm(instr_use_truth + wikipedia_extract + " " + instr_find_mistakes + initial_response + " " + instr_print_necessary)
    return corrected_response

text = process_response("Titanic is a 1997 American film directed by James Cameron. IIt is based on accounts of the sinking of RMS Titanic and stars Natalie Portman and Hugh Laurie as members of different social classes")
print(text)

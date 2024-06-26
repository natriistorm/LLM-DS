# 'Is there any factual mistakes in this fragment of text? If no, please check Wikipedia article about it.'

# Correct the mistakes in this fragment and print the corrected fragment.

# Here's a small database. If the following text is incorrect,
# correct the mistakes in the text using this database and print the corrected fragment.
import re
from src.ask_llm import ask_llm
from src.do_search import do_search
from src.styles import styleResponse, listResponse, addMoreContext, summarizeResponse, searchWikipediaForProof, \
    shortenResponse

entities_re = re.compile("entities")

'''
PROMPTS
'''

# 1. Ask to map the entities from response
instr_map_entities = "Can you extract the entities from this fragment: "

# 2.1 Correct the factual mistakes in text
instr_find_mistakes = "You need to find and fix facts in the fragment, that contradicts known information. Here is an original fragment: "

# 2.2 Using fragment as ground truth information
instr_use_truth = "Known information: "

# 3. Ask LLM how we should look for Wikipedia page
instr_wikipedia_page = "What should I type into Google Search if I want to find Wikipedia article with information considered in this fragment: "

# 4. Print only stated info
instr_print_necessary = "Print the original fragment with just fixed factual errors and without information to the fragment not mentioned in that initially"

# response_to_fix = "Titanic is a 1997 American film directed by James Cameron." \
#                   " It is based on accounts of the sinking of RMS" \
#                   "Titanic and stars Natalie Portman and Hugh Laurie as members of different social classes"
true_info = " Main characters of the film Abac are portrayed by Lucy Korolla and Terens Yokohama. The film was made in 2008 and won severl Oscars"
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


def compare_entities(initial_response: str, internet_search_response: str):
    text_with_entities = ask_llm(instr_map_entities + initial_response)
    initial_entities_lst = process_entities(text_with_entities)  # these entities may be possibly all wrong
    internet_search_entities = ask_llm(instr_map_entities + internet_search_response)
    internet_search_entities_lst = process_entities(internet_search_entities)
    initial_set = set(initial_entities_lst)
    internet_set = set(internet_search_entities_lst)
    difference = initial_set.difference(internet_set)
    print(difference)


def process_with_provided_knowledge(initial_response: str, provided_knowledge) -> str:
    corrected_response = ask_llm(
        instr_find_mistakes + initial_response + "\n" + instr_use_truth + provided_knowledge + "\n" + instr_print_necessary)
    return corrected_response


def define_main_topic(suggested_response: str) -> str:
    main_topic_instr = "Can you give main topic of this fragment? "
    main_topic_answer = ask_llm(main_topic_instr + suggested_response)
    sentences_of_answer = main_topic_answer.split('.')
    if sentences_of_answer[0].startswith("The main topic of this fragment is"):
        main_topic = sentences_of_answer[0][35:]
    else:
        for sent in sentences_of_answer:
            if sent.lower().find("main topic is") >= 0:
                idx = sent.find("main_topic is")
                main_topic = sent[idx + len("main_topic is") + 1]
                break
        else:
            raise ValueError("LLM did not provided main topic of response")
    return main_topic


def ask_to_fix(matcher) -> str:
    rating = matcher.group()
    if 4 <= int(rating) <= 5:
        return "ok"
    else:
        # let's ask how to fix that
        fix_instr = "How would you fix this response? Print an example"
        fixed_resp = ask_llm(fix_instr)
        if len(fixed_resp) > 2000:
            fixed_resp = shortenResponse(fixed_resp, 500)
        return fixed_resp


def ask_for_feedback_about_response(suggested_response: str, main_topic: str) -> str:
    feedback_instr = f"Do you think this is a good response to a question about \"What is {main_topic}?\" to a person, who know nothing about it?  The response: "
    rate_instr = "From 1 to 5 where 1 is not comprehensive response and 5 is a very good response how good is this response?"
    llm_opinion = ask_llm(feedback_instr + suggested_response + rate_instr)
    digits_in_text = re.findall("\d{1}", llm_opinion)
    if len(digits_in_text) == 0:
        raise Exception("Model cannot rate this response for some reason. Try again later")
    else:
        # let's think first digit appearing in response i
        rating = int(digits_in_text[0])
        if 4 <= int(rating) <= 5:
            return "ok"
        else:
            # let's ask how to fix that
            fix_instr = "How would you fix this response? Print an example"
            fixed_resp = ask_llm(fix_instr)
            if len(fixed_resp) > 2000:
                fixed_resp = shortenResponse(fixed_resp, 500)
            return fixed_resp


# style = ["list", "long", "short", "search", "summarize"]
def launcher(initial_response, style=None, params=None):
    if style is None:
        response = styleResponse(initial_response)
    elif style == "list":
        response = listResponse(initial_response, *params)
    elif style == "short" or style == "summarize":
        response = summarizeResponse(initial_response)
    elif style == "long":
        response = addMoreContext(initial_response, *params)
    elif style == "search":
        response = searchWikipediaForProof(initial_response)
    else:
        raise Exception("Invalid style option")
    suggested_response = response.process()
    # let's get main idea
    try:
        main_idea = define_main_topic(suggested_response)
    except Exception as exception:
        print(exception)
        return -1
    opinion = ask_for_feedback_about_response(suggested_response, main_idea)
    if opinion == "ok":
        return suggested_response
    else:
        return opinion


def provide_llm_with_action(question: str, answer: str):
    actions_instr = f"Here's actions you can do: fix the factual errors, add more context to response, delete unnecessary information from response, make it more eloquent. User would like to get the best response on question: \"{question}\". The response is {answer}. Choose several actions you would do to enhance this particular response? List the necessary actions and print final corrected response. If you fix an error, don't mention incorrect information. Make as short response as possible. If everything is alright with initial response, don't do anything."
    llm_opinion = ask_llm(actions_instr)
    listed_actions = re.findall("^- \w*$", llm_opinion)
    idx_of_response = llm_opinion.lower().find('corrected response:')
    if idx_of_response >= 0:
        corrected_response = llm_opinion[idx_of_response + len('corrected response:'):]
    else:
        corrected_response = answer
    return llm_opinion.replace('\"', "")


print(provide_llm_with_action("What is scrum of scrums", "spectacle"))

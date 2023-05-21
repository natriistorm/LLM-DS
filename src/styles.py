import re

from .ask_llm import ask_llm
from .do_search import do_search


# list of important information
# just basic response
# only essential information (i.e we are not interested how many oscard won titanic, we need only starring actors)
# essay-style
class styleResponse:
    def __init__(self, response):
        self.initial_resp = response
        self.final_resp = None

    def process(self, continue_conv=False):
        pass


class listResponse(styleResponse):
    def __init__(self, response, size_of_list=None):
        super().__init__(response)
        self.size_of_list = size_of_list

    def get_size_of_list(self, inter_resp):
        bullets = inter_resp.split("\n- ")[1:]
        return len(bullets)

    def process(self, continue_convo=False):
        list_format_instr = "Can you format important information from this text into a bulleted list? "
        intermidiate_resp = ask_llm(list_format_instr + self.initial_resp)

        if self.size_of_list is not None:
            number_of_bullers = self.get_size_of_list(intermidiate_resp)
            if number_of_bullers > self.size_of_list:
                shrink_instr = f"Can you make it up to {self.size_of_list} bullet points?"
                shrinked_resp = ask_llm(shrink_instr)
                final_resp = shrinked_resp
            else:
                final_resp = intermidiate_resp
        else:
            final_resp = intermidiate_resp
        return final_resp


class summarizeResponse(styleResponse):

    def process(self, continue_convo=False) -> str:
        if continue_convo is True:
            # we continue the conversation, no need to repeat response
            summarize_instr = "Can you summarize it?"
        else:
            summarize_instr = f"Can you summarize this fragment? {self.initial_resp}"

        summarized_resp = ask_llm(summarize_instr)
        return summarized_resp


class addMoreContext(styleResponse):

    def __init__(self, response: str, context_len: int):
        super().__init__(response)
        self.size_of_context = context_len

    def process(self, continue_convo=False):
        if continue_convo is True:
            # we continue the conversation, no need to repeat response
            more_context_instr = f"Can you add more context to it? Make it in {self.size_of_context} sentences"
        else:
            more_context_instr = f"I want you to add more information in following fragment. Information, already presented in it should stay untouched," \
                                 f" also don't repeat information from the text. Make it no longer then {self.size_of_context} symbols." \
                                 f" Here's a fragment: {self.initial_resp}"
        more_context_resp = ask_llm(more_context_instr)
        llm_response = remove_stop_words(more_context_resp)
        return self.initial_resp + llm_response


class shortenResponse(styleResponse):
    def __init__(self, response, desired_len):
        super().__init__(response)
        self.response_len = desired_len

    def process(self, response_to_process=None):
        shorten_instr = "Can you make it shorter?"
        response_by_llm = ask_llm(shorten_instr)
        processed_response = extract_actual_response(response_by_llm)
        while len(processed_response) > self.response_len:
            shorten_instr = "Can you make it more short?"
            response_by_llm = ask_llm(shorten_instr)
            processed_response = extract_actual_response(response_by_llm)
        return processed_response


class searchWikipediaForProof(styleResponse):
    def __init__(self, response):
        super().__init__(response)

    def extract_wikipedia_page(self, wikipedia_response: str) -> str:
        suggested_search = wikipedia_response.split("\"", 2)[1]
        return suggested_search

    def extract_corrected_response(self, repsonse: str) -> str:
        suggested_response = repsonse.split("\"", 2)[1]
        return suggested_response

    def process(self, response_to_process=None):
        # diving into wikipedia...
        instr_wikipedia_page = "What should I type into Google Search if I want to find Wikipedia article with information considered in this fragment: "
        wikipedia_response = ask_llm(instr_wikipedia_page + self.initial_resp)
        search = self.extract_wikipedia_page(wikipedia_response)
        # now diving into google search
        wikipedia_extract = do_search(f"{search}")
        # let's ask llm
        # at first -> shorten context
        summarized_wiki_extract = summarizeResponse(wikipedia_extract).process()
        instr_use_truth = "Known information: "
        instr_find_mistakes = "You need to find and fix facts in the fragment, that contradicts known information. Here is an original fragment: "
        instr_print_necessary = "Print the original fragment with just fixed factual errors and without information to the fragment not mentioned in that initially"
        corrected_response = ask_llm(
            instr_find_mistakes + self.initial_resp + "\n" + instr_use_truth +
            summarized_wiki_extract + "\n" + instr_print_necessary)
        return corrected_response


def remove_stop_words(response: str) -> str:
    response = re.sub("Sure!", "", response)
    response = re.sub("Here's\w*:\n", "", response)
    response = re.sub("Sure, here's\w*:\n", "", response)
    return response


def extract_actual_response(response_to_process) -> str:
    response_by_llm = response_to_process.split(":\n\"")[1]
    if response_by_llm.find("\"\n") >= 0:
        response_by_llm = response_by_llm.split("\"\n")[0]
    return response_by_llm

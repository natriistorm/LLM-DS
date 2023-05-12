import re

from ask_llm import ask_llm


# list of important information
# just basic response
# only essential information (i.e we are not interested how many oscard won titanic, we need only starring actors)
# essay-style
class styleResponse:
    def __init__(self, response):
        self.initial_resp = response
        self.final_resp = None

    def process(self, response_to_process=None):
        pass


class listResponse(styleResponse):
    def __init__(self, response, size_of_list=None):
        super().__init__(response)
        self.size_of_list = size_of_list

    def get_size_of_list(self, inter_resp):
        bullets = inter_resp.split("\n- ")[1:]
        return len(bullets)

    def process(self, response_to_process=None):
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
            summarize_instr = f"Can you summirize this fragment? {self.initial_resp}"

        summarized_resp = ask_llm(summarize_instr)
        return summarized_resp


class addSomeContext(styleResponse):
    def process(self, continue_convo=False):
        if continue_convo is True:
            # we continue the conversation, no need to repeat response
            more_context_instr = "Can you add more context to it?"
        else:
            more_context_instr = f"I want you to add more information in following fragment. However, " \
                                 f"the information, already presented in it should stay untouched," \
                                 f" don't change or delete it. Also don't repeat information from the text. Here's a fragment: {self.initial_resp}"
        more_context_resp = ask_llm(more_context_instr)
        llm_response = remove_stop_words(more_context_resp)
        return self.initial_resp + llm_response


def remove_stop_words(response: str) -> str:
    response = re.sub("Sure!", "", response)
    response = re.sub("Here's\w*:\n", "", response)
    response = re.sub("Sure, here's\w*:\n", "", response)
    return response

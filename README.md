# LLM-DS

Part of future model of the Dialogue Flow Framework from DeepPavlov.

This is drafts of the model, that doublechecks the information with Wikipedia and cooperate with ChatGPT to provied best response

Pipeline:

1. You provide some response, you would like to double-check
*Note*: we will add functionality to generate response, but then you will need the question, you would like to know from LLM

2. LLM is asked, what Wikipedia page suits better for check the information from the response. If the information cannot be checked from opened sources, you're expected to provide some truth information

3. LLM is asked to fix the errors in the suggested fragments with the information it scrapped from Wikipedia

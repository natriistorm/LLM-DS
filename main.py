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
import openai

find_mistakes_instruction = "Correct the mistakes in this fragment and print the corrected fragment."

openai.api_key = "TOKEN"

response_to_fix = "Titanic is a 1997 American film directed by James Cameron." \
                  " It is based on accounts of the sinking of RMS" \
                  "Titanic and stars Natalie Portman and Hugh Laurie as members of different social classes"

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": f"{find_mistakes_instruction}: {response_to_fix}"},
    ]
)

database_connection = " "
search_engine_llm = " "

result = ''
for choice in response.choices:
    result += choice.message.content

print(result)

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from config import OPENAI_API_KEY


model = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    temperature=0,
    model_name='gpt-4o-mini',
    openai_api_base="https://api.proxyapi.ru/openai/v1"
)


# Промпт для парсинга информации о кастингах из сообщений
prompt_text = """
Ты профессиональный повар. К тебе обращаются люди для того, что бы подсказал им рецепт для блюда из имеющихся у них
продуктов. Рецепт должен быть строго из того списка продуктов, который предоставит пользователь, только если он сам не
попросить тебя дать рецепт из любых продуктов. По каждому запросу нужно давать три рецепта.
Запрос пользователя: {input}
"""
prompt = PromptTemplate.from_template(prompt_text)


async def ai_recipe(user_products_str):
    """Процесс запроса к ИИ"""
    ai_chain = prompt | model
    recipe_from_ai = await ai_chain.ainvoke({'input': user_products_str})
    return recipe_from_ai.content


if __name__ == '__main__':
    import asyncio
    from langchain_core.messages import HumanMessage, AIMessage
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    prompt_text = """
    Ты помощник разработчика на языке python. Отвечай на вопросы максимально точно и емко.
    """
    prompt = ChatPromptTemplate.from_messages([
        ('system', prompt_text),
        MessagesPlaceholder(variable_name='chat_history'),
        ('human', '{input}')
    ])
    # .bind_tools([{"type": "web_search_preview"}])
    chain = prompt | model
    chat_history = []

    async def process_chat(user_input, chat_history_list):

        response = await chain.ainvoke({
            'input': user_input,
            # История чата отключается через пустой список
            'chat_history': chat_history_list,
        })
        return response.content


    async def start_up():
        while True:
            user = input('You: ')
            if user != 'exit':
                res = await process_chat(user, chat_history)
                print(res)
                chat_history.append(HumanMessage(content=user))
                chat_history.append(AIMessage(content=res))
            else:
                break

    asyncio.run(start_up())

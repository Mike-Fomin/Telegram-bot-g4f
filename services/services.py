import traceback
from g4f.client import Client
from g4f.client.stubs import ChatCompletion


client = Client()

def get_chatgpt_response(message_data: list[dict[str, str]]) -> str:
    while True:
        try:
            response: ChatCompletion = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=message_data,
                web_search=False
            )
        except:
            traceback.print_exc()
        else:
            break

    return response.choices[0].message.content


def run_in_thread(arg: str):
    return get_image_response(arg)


def get_image_response(message_data: str) -> str:
    response = client.images.generate(
        model="flux",
        prompt=message_data,
        response_format="url"
    )
    return response.data[0].url

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OPEN_API_KEY"),
)


chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are the assistant of an application that helps uses categorize the things they did each day. Parse the data sent by the user and return a list the category names that are represented by their actions, if any. Only respond with a list of the category names.",
        },
        {
            "role": "system",
            "content": "The user has created the following categories: 'Protein', 'Running', 'Sleep', 'Productivity', 'Mood' ",
        },
        {
            "role": "user",
            "content": "I had a 180g of protein and went for a 5km run. I also worked on my project for 3 hours. I felt happy today.",
        }
    ],
    model="gpt-4-0125-preview",
    # response_format={ "type": "json_object" }
)

print(chat_completion.choices[0].message.content)
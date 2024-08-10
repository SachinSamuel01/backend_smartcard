from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os

import warnings
warnings.filterwarnings("ignore")

load_dotenv()


llm_key= os.getenv('LLM_KEY')

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001",google_api_key=llm_key)

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    temperature=0.3,
    top_p=0.9,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=llm_key
)




prompt_template='''
You are an AI assistant. 

Instructions: {prompt}
Reference Data: {content}
Conversation History: {chat}
User's Question: {query}

Respond concisely, continuing the conversation.
'''

prompt= PromptTemplate.from_template(prompt_template)
parser= StrOutputParser()

chain= prompt | llm | parser

def get_response(prompt,content,chat,query ):
    
    res= chain.invoke(
        {
        'prompt': prompt,   
        'content': content,
        'chat': chat,
        'query': query
        }
    )
    return res


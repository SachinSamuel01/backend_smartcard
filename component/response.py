from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings


# from langchain.agents import Agent
# from langchain.chains import JSONChain, XMLChain


from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent

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

Respond very concisely, continuing the conversation.
'''

prompt= PromptTemplate.from_template(prompt_template)
parser= StrOutputParser()

chain= prompt | llm | parser



def create_csv_agent_from_llm(csv_path_lst):
    
    csv_agent= create_csv_agent(
        llm,
        csv_path_lst,
        allow_dangerous_code=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
       
    )

    return csv_agent




def doc_agent_response(prompt,content,chat,query ):
    
    res= chain.invoke(
        {
        'prompt': prompt,   
        'content': content,
        'chat': chat,
        'query': query
        }
    )
    return res

def csv_agent_reponse(csv_agent, query):
    return csv_agent.run(query)


# class JSONAgent(Agent):
#     def __init__(self, llm, json_data: dict):
#         self.llm = llm
#         self.chain = JSONChain(llm)
#         self.json_data = json_data

#     def run(self, query: str):
#         output = self.chain.run(self.json_data, query)
#         return output


# class XMLAgent(Agent):
#     def __init__(self, llm, xml_data: str):
#         self.llm = llm
#         self.chain = XMLChain(llm)
#         self.xml_data = xml_data

#     def run(self, query: str):
#         output = self.chain.run(self.xml_data, query)
#         return output
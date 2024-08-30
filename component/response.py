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

from langchain.agents import (
    create_json_agent,
    AgentExecutor
)
from langchain.agents.agent_toolkits import JsonToolkit
from langchain.tools.json.tool import JsonSpec
from langchain.schema import SystemMessage
from langchain.tools import BaseTool
import json
from typing import Dict, List, Any, Union

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
    max_retries=6,
    api_key=llm_key
)




prompt_template='''
You are an AI assistant. 

Instructions: {prompt}
Reference Data: {content}
Conversation History: {chat}
User's Question: {query}

Your response should be concise and accurate to the query.
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


def create_json_agent_from_llm(json_data):
    json_spec = JsonSpec(dict_=json_data, max_value_length=8000)
    json_toolkit = JsonToolkit(spec=json_spec)

    json_agent = create_json_agent(
        llm=llm,
        toolkit=json_toolkit,
        verbose= True
    )
    return json_agent


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


def json_agent_response(json_agent, query):
    return json_agent.run(query)




# test ------------------------------

def analyze_json_structure(data: Any, path: str = "root") -> str:
    if isinstance(data, dict):
        return f"{path} (dict): " + ", ".join([f"{k}: {analyze_json_structure(v, f'{path}.{k}')}" for k, v in data.items()])
    elif isinstance(data, list):
        return f"{path} (list[{len(data)}]): " + analyze_json_structure(data[0] if data else None, f"{path}[0]")
    else:
        return f"{path} ({type(data).__name__})"

class JsonStructureAnalyzer(BaseTool):
    name = "json_structure_analyzer"
    description = "Analyzes and returns the structure of the JSON data"
    json_data: Dict[str, Any]

    def _run(self, query: str) -> str:
        return analyze_json_structure(self.json_data)

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("JsonStructureAnalyzer does not support async")

def create_enhanced_json_agent(json_data: Dict[str, Any], model: str = "gpt-3.5-turbo"):
    json_spec = JsonSpec(dict_=json_data, max_value_length=8000)
    json_toolkit = JsonToolkit(spec=json_spec)

    structure_analyzer = JsonStructureAnalyzer(json_data=json_data)
    tools = json_toolkit.get_tools() + [structure_analyzer]

    

    system_message = SystemMessage(
        content="You are an AI assistant specializing in JSON data analysis. "
                "Always start by analyzing the structure of the JSON data using the json_structure_analyzer tool. "
                "Use this information to navigate and query the JSON data effectively."
    )

    json_agent = create_json_agent(
        llm=llm,
        toolkit=JsonToolkit(spec=json_spec),
        verbose=False,
        extra_tools=[structure_analyzer],
        system_message=system_message
    )

    return json_agent

def query_json_agent(agent, query: str) -> str:
    try:
        return agent.run(query)
    except Exception as e:
        return f"An error occurred: {str(e)}"

# end ---------------------------------


# from vectordb import load_json_files

# path= r'D:\projects\VS_code\internships\smartcard_python\test_uploads\json_data'

# data= load_json_files(path)
# # agent= create_json_agent_from_llm(data)
# # response= json_agent_response(agent,'tell me all the patients conditions')
# # print(response)

# agent= create_json_agent_from_llm(data)
# response= json_agent_response(agent, 'what is the value of chest')
# print(response)

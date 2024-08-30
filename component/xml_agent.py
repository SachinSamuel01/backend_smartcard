import os
import xml.etree.ElementTree as ET
from typing import Dict, List

from langchain.schema import HumanMessage, SystemMessage

from component.response import llm

class SimpleXMLAgent:
    def __init__(self, directory: str):
        self.xml_files: Dict[str, ET.Element] = {}
        self.load_xml_files(directory)
        self.llm = llm

    def load_xml_files(self, directory: str):
        for filename in os.listdir(directory):
            if filename.endswith('.xml'):
                file_path = os.path.join(directory, filename)
                try:
                    tree = ET.parse(file_path)
                    self.xml_files[filename] = tree.getroot()
                except ET.ParseError as e:
                    print(f"Error parsing {filename}: {e}")

    def analyze_structure(self, filename: str) -> str:
        if filename not in self.xml_files:
            return f"File {filename} not found."
        
        def _analyze_element(element: ET.Element, depth: int = 0) -> str:
            result = "  " * depth + element.tag
            if element.attrib:
                attrs = ", ".join(f"{k}='{v}'" for k, v in element.attrib.items())
                result += f" ({attrs})"
            result += "\n"
            for child in element:
                result += _analyze_element(child, depth + 1)
            return result

        return _analyze_element(self.xml_files[filename])

    def xpath_query(self, filename: str, xpath: str) -> List[str]:
        if filename not in self.xml_files:
            return [f"File {filename} not found."]
        
        elements = self.xml_files[filename].findall(xpath)
        return [ET.tostring(elem, encoding='unicode').strip() for elem in elements]

    def list_files(self) -> List[str]:
        return list(self.xml_files.keys())

    def query(self, user_query: str) -> str:
        system_message = SystemMessage(content="""You are an AI assistant specializing in XML data analysis. 
        You can analyze XML structures, perform XPath queries, and answer questions about XML files. 
        Use the provided information to answer the user's query.""")

        context = f"Available XML files: {', '.join(self.list_files())}\n\n"
        context += "XML structures:\n"
        for filename in self.xml_files:
            context += f"{filename}:\n{self.analyze_structure(filename)}\n"

        human_message = HumanMessage(content=f"{context}\nQuery: {user_query}")

        response = self.llm([system_message, human_message])
        return response.content

# Example usage
# if __name__ == "__main__":
#     directory = r'D:\projects\VS_code\internships\smartcard_python\test_uploads\xml_data'
#     agent = SimpleXMLAgent(directory)

#     queries = [
#         "List all the XML files available.",
#         "What is the structure of the file 'example.xml'?",
#         "Find all book titles in 'library.xml'.",
#         "What are the common elements across all XML files?",
#         "what are the files about"
#     ]

#     for query in queries:
#         print(f"\nQuery: {query}")
#         result = agent.query(query)
#         print(f"Result: {result}")
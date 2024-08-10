from langchain_community.vectorstores import Qdrant
import qdrant_client
import os, shutil
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyMuPDFLoader, PyPDFLoader
from langchain_community.document_loaders.unstructured import UnstructuredFileLoader


import warnings
warnings.filterwarnings("ignore")

# from response import embeddings
from component.response import embeddings
load_dotenv()
qdrant_host= os.getenv('QDRANT_HOST')
qdrant_key= os.getenv('QDRANT_KEY')

# size=768

client= qdrant_client.QdrantClient(
    url=qdrant_host,
    api_key=qdrant_key
)

vector_config= qdrant_client.http.models.VectorParams(
    size= 768,
    distance= qdrant_client.http.models.Distance.COSINE
)

files_already_exists_path= r'./uploads/filesUploads'

collection_dir= set(os.listdir(files_already_exists_path))




def create_vectorstore(collection_name):
    global collection_dir
    if collection_name not in collection_dir:
    
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=vector_config
        )

        collection_dir.add(collection_name)

    vector_store = Qdrant(
        client=client, 
        collection_name=collection_name, 
        embeddings=embeddings,
    )

    return vector_store

def append_data_vectorstore(vector_store,collection_path):
   # loader= DirectoryLoader(collection_path,glob="**/*.txt" ,loader_cls=TextLoader)
    loader= DirectoryLoader(collection_path,glob="**/*.pdf" ,loader_cls=PyPDFLoader)
    documents= loader.load()

    text_splitter= RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100, length_function= len)
    docs=text_splitter.split_documents(documents)

    vector_store.add_documents(docs)

    



def vector_store_to_retriever(vector_store):
    return vector_store.as_retriever()

def retrieve_content(retriever,query):
    
    docs=retriever.invoke(query)
    content=docs[0]
    
    return content



def delete_collection(collection_name):
    client.delete_collection(collection_name=collection_name)
    dir= os.path.join(files_already_exists_path,collection_name)
    shutil.rmtree(dir)
    









# collection_name = "example_collection"
# collection_path = "D:\projects\VS_code\project\RAG_with_Open_Source_LLM_and_LangChain"  # Update with the actual path
# vector_store = create_vectorstore(collection_name)
# append_data_vectorstore(vector_store, collection_path)
# retriever = vector__retriever(vector_store)

# print(retriever)
# query = "tell me the contents provided to you"
# content = retrieve_content(retriever, query)
# print(f"Retrieved content: {content}")
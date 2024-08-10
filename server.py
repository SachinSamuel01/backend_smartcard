from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import shutil
from pydantic import BaseModel
import json
import warnings
warnings.filterwarnings("ignore")

from component.vectordb import create_vectorstore, append_data_vectorstore, retrieve_content, vector_store_to_retriever, delete_collection
from component.response import get_response
from component.webcrawling import scrape_and_save_links

app = FastAPI()

BASE_DIR = "./uploads/filesUploads"

chat_lst=[]








vector_retriever= None

counter=0

prompt=''' 
Follow these principles in your interactions:

1. **Consultative Approach:**
2. **Tailored Recommendations:** 
3. **Detailed Information:** 
4. **Comparison:** If applicable
5. **Value-Added Services:** 
6. **Proactive Assistance:** 
7. **Gratitude and Follow-Up:**  
'''
# prompt= '''
# based on the content generate response in paragraph form
# '''

# End of conversation it should ask customer to fill in contact form : name, email, phone, Company


class UploadRequest(BaseModel):
    name: str
    links: Optional[str] = None


@app.post("/upload")
async def upload_files(
    
    files: List[UploadFile] = File(None),
    json_data: Optional[str] = Form(...),
):
    data = json.loads(json_data)
    request = UploadRequest(**data)

    name= request.name
    links= request.links
    
    collection_dir = os.path.join(BASE_DIR, name)
    if not os.path.exists(collection_dir):
        os.makedirs(collection_dir)
    
    print(links)

    # Save uploaded files
    if files:
        for file in files:
            file_path = os.path.join(collection_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

    # Process web links
    print(links)
    
    if links:
        links_list = [link.strip() for link in links.split("\n") if link.strip()]
        if links_list:
            scrape_and_save_links(links_list, collection_dir)

    # Create vector store (assuming this is defined elsewhere in your code)
    
    vector_store = create_vectorstore(name)
    append_data_vectorstore(vector_store,collection_dir)

    return JSONResponse(status_code=200, content={"message": "Files and links uploaded successfully."})

@app.get("/collections/")
async def get_collections():
    if not os.path.exists(BASE_DIR):
        return []
    
    collections = []
    for folder_name in os.listdir(BASE_DIR):
        collections.append({"name": folder_name})

    return collections

@app.get("/collections/{name}/deploy")
async def deploy_collection(name: str):
    global vector_retriever
    # collection_dir = os.path.join(BASE_DIR, name)
    # vector_store= create_vectorstore(name)
    vector_store = create_vectorstore(name)
    retriever= vector_store_to_retriever(vector_store)
    vector_retriever= retriever.copy()

    collection_dir = os.path.join(BASE_DIR, name)
    if not os.path.exists(collection_dir):
        raise HTTPException(status_code=404, detail="Collection not found")

    files = [os.path.join(collection_dir, f) for f in os.listdir(collection_dir)]

    chat_lst.clear()
    
    vector_db = {f: "Vector representation of {}".format(f) for f in files}
    return {"vector_db": vector_db, "message": f"Collection {name} deployed"}


@app.post("/collections/delete")
async def delete_data_collection(request:dict):
    name= request.get('name')
    delete_collection(name)
    return JSONResponse(status_code=200, content={"message": f"The collection {name} is deleted."})


@app.post("/query/")
async def process_query(request: dict):
    
    collection = request.get("collection")
    query = request.get("query")
    
    
    content=retrieve_content(vector_retriever,query)

    if chat_lst==[]:

        response= get_response(prompt,content,'NONE', query)
        chat= f'Query: {query}\nResponse: {response}'
        chat_lst.append(chat)

    else:
        last_chat=''
        for i in chat_lst:
            last_chat= last_chat+i+'\n'
        response= get_response(prompt,content,'NONE', query)
        chat= f'Query: {query}\nResponse: {response}'
        chat_lst.append(chat)

    
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

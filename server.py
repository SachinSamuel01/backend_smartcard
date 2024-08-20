from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import shutil
from pydantic import BaseModel
import json
import re
import glob
from fastapi.middleware.cors import CORSMiddleware

import warnings
warnings.filterwarnings("ignore")

from component.vectordb import create_vectorstore, append_data_vectorstore, retrieve_content, vector_store_to_retriever, delete_collection
from component.response import doc_agent_response, create_csv_agent_from_llm, csv_agent_reponse
from component.webcrawling import scrape_and_save_links
from component.reading_cards import get_text_from_img

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000", "https://pdf-chat-nu-green.vercel.app/","https://pdf-chat-nu-green.vercel.app/backend-testing"],  # Be more specific in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = "./uploads/filesUploads"
IMG_UPLOAD_DIR=r'./uploads/cardUploads'

chat_lst=[]

vector_retriever= None
csv_agent= None



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

prompt2 ='''
You will be given text extracted from an image of a card in the Reference Data, which could be a business card, credit card, driver's license, or any other type of identification card. 

Your task is to analyze the text and extract relevant information, structuring it into a Python dictionary.

The dictionary should have the following keys, if applicable based on the type of card:

* `name` 
* `company` (for business cards)
* `designation` (for business cards)
* `card_number` (for credit cards, driver's licenses, etc.)
* `expiry_date` (for credit cards)
* `issue_date` (for driver's licenses)
* `phone_number`
* `website`
* `email`
* `address` 

The values for these keys should be the corresponding information extracted from the text. 

**Please note:**

* If any of the information is missing from the text, the corresponding value in the dictionary should not exist`.
* Ensure the extracted information is accurate and free of any extra characters or symbols.
* Prioritize extracting key information that is relevant to the type of card detected.

Now, process the following text and provide the structured dictionary:

'''
prompt_img='''
**Task:** 
Extract structured data from text extracted from an image of a card (business card, credit card, driver's license, etc.).

**Output Format:**
Python dictionary with the following keys (if applicable): 

* `name` 
* `company` 
* `designation` 
* `card_number` 
* `expiry_date`
* `issue_date` 
* `phone_number`
* `website`
* `email`
* `address` 


* If information is missing, set the corresponding value to `None`.
* Ensure extracted information is accurate and clean.
* Prioritize key information relevant to the detected card type.
* Also provide the output in pretty print
'''

prompt3='''
**Task:** 
You'll be provided with text extracted from an image of various card types (business card, credit card, debit card, driver's license, PAN card, etc.). 

**Objective:** 
Analyze the text, identify the card type, and extract relevant information. Structure the extracted data into a Python dictionary as Json Pretty Print.

**Output Format:**

* A string that represents the extracted data in a visually formatted way, resembling the output of Python's `pprint` function.
* Keys: Relevant designations based on the card type (e.g., `name`, `address`, `card_number`, etc.)
* Values: Corresponding information extracted from the text
* If information is missing, set the value to `None`.
* Ensure extracted information is accurate and free of extra characters/symbols

'''

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
    
    pdf_lst= glob.glob(f"{collection_dir}/*.pdf")
    if len(pdf_lst)!=0:
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
    global csv_agent
    
    collection_dir = os.path.join(BASE_DIR, name)
    pdf_lst= glob.glob(f"{collection_dir}/*.pdf")
    if len(pdf_lst)!=0:

        vector_store = create_vectorstore(name)
        retriever= vector_store_to_retriever(vector_store)
        vector_retriever= retriever.copy()

    else:
        vector_retriever= None
    
    csv_lst= glob.glob(f"{collection_dir}/*.csv")
    
    if len(csv_lst)!=0:
        csv_agent= create_csv_agent_from_llm(csv_lst)
    else:
        csv_agent= None
    
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
    
    # collection = request.get("collection")
    query = request.get("query")
    response=''
    if vector_retriever != None:
        content=retrieve_content(vector_retriever,query)

        if chat_lst==[]:

            response= doc_agent_response(prompt,content,'NONE', query)
            chat= f'Query: {query}\nResponse: {response}'
            chat_lst.append(chat)

        else:
            last_chat=''
            for i in chat_lst:
                last_chat= last_chat+i+'\n'
            response= doc_agent_response(prompt,content,'NONE', query)
            chat= f'Query: {query}\nResponse: {response}'
            chat_lst.append(chat)

    if csv_agent != None:
        response= csv_agent_reponse(csv_agent, query)

    
    return {"response": response}


@app.post("/upload_image/")
async def upload_image(image: UploadFile = File(...)):
    # Get the original filename from the uploaded file
    
    
    filename = image.filename

    # Check if a file with the same name already exists
    if os.path.exists(os.path.join(IMG_UPLOAD_DIR, filename)):
        return JSONResponse(content={"error": "File with same name already exists"}, status_code=409)

    # Save the file to the specified directory with its original filename
    file_path = os.path.join(IMG_UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    text_from_img = get_text_from_img(file_path)
    response= doc_agent_response(prompt3,text_from_img,'NONE', 'NONE')
    pattern = r'\{[^}]*\}'
    match = re.search(pattern, response, re.DOTALL)
    
    response= match.group()

    
    json_content= eval(response)

    
    # with open(os.path.join(IMG_UPLOAD_DIR,'card_data.json'), 'a') as f:
    #     json.dump(json_content,f)
    
    return {"response": response}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

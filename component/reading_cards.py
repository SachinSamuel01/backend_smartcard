import requests
from dotenv import load_dotenv
import os
import json

import warnings
warnings.filterwarnings("ignore")

load_dotenv()

def extract_text_from_image(image_path, code, username, url):
    
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
        
    r = requests.post(url, data=image_data, auth=(username, code))

    if r.status_code == 401:
        #Please provide valid username and license code
        return "Your license code is not valid and has used total no. of usage"

    # Decode Output response
    jobj = json.loads(r.content)
    

    ocrError = jobj["ErrorMessage"]
    ocrError= str(ocrError)

    if ocrError != '':
            #Error occurs during recognition
            return f"Recognition Error: {ocrError}"
            


    return str(jobj["OCRText"][0][0])




ocr_code=os.getenv('OCR_CODE')
ocr_username= os.getenv('OCR_USERNAME')
ocr_url=os.getenv('OCR_URL')



def get_text_from_img(img_path):

    
    
    
    extracted_text = extract_text_from_image(img_path, ocr_code, ocr_username, ocr_url)
    if extracted_text:
        
        return extracted_text
    else:
        return "Text extraction failed."
    

# FilePath = r"D:\projects\VS_code\internships\smartcard_python\test_uploads\WhatsApp Image 2024-08-13 at 15.37.36 (1).jpeg"
# text= get_text_from_img(FilePath)
# print(text)
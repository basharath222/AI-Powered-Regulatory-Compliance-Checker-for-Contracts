from google import genai
from pydantic import BaseModel
import json
import PyPDF2
import os
from groq import Groq
from dotenv import load_dotenv
from google.genai import types
import notification

load_dotenv()

# ********   Phase 1    ******** #
def Clause_extraction(file):
    print("inside clause extraction")
    class ClauseExtraction(BaseModel):
        clause_id: str
        heading: str
        text: str
    
    text=""
    with open(file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
         
    client = genai.Client(api_key=os.getenv("gemini_api_key"))

  
    prompt = f"""
    you are an expert in legal contract analysis.
    Your task is to extract all **clauses** from the following contract text.
    
    ### Guidelines:
    - A clause may begin with:
    - A number/letter (e.g. "1.", "A."),
    - The word "Clause" followed by a number (e.g. "Clause 1", "Clause 5"), OR
    - An ALL CAPS heading (e.g. "DEFINATION", "TRANSFER OF DATA".)
    
    -Each extracted clause must include:
    -**clause_id** (the exact numbering/label from the contract e.g. "1.", "A.", "Clause 1", "EXHIBIT A" etc)
    -**heading/title** (use the explicit heading if present; if absent, use the first few words of the clause as a makeshift title)
    -**full text** (the complete text of the clause, including any sub-clauses, preserving legal wording exactly as in the contract)
    
    -Maintain clause boundaries percisly. do not merge multiple clauses into one.
    -Include clauses from exhibits, appendices, and annexes if present.
    -Do not omit any content unless it is clearly not-contractual (e.g. page numbers, headers, footers, blank sihnature lines).
    -response in **valid json** only (no explanation, no notes, no extra text).
    
    Input: {text}
    
    Response in this JSON Structure:
    [
        {{
            "clause_id": "<clause_id>",
            "heading/title": "<heading_or_title>",
            "full text": "<full_text_of_clause>"
        }},
        ...
    ]
    """
    response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking
                response_mime_type="application/json",
                response_schema=list[ClauseExtraction],
            ),
            
        )
    response= response.text
    
    return response


def Clause_extraction_with_summarization(file, agreement_type=None):
    print("inside clause extraction")
    class ClauseExtraction(BaseModel):
        clause_id: str
        heading: str
        summarised_text: str
    
    text=""
    with open(file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
         
    client = genai.Client(api_key=os.getenv("gemini_api_Key"))

    
    prompt = f"""
    you are an expert in legal contract analysis.
    Your task is to extract all **clauses** from the following contract text and summarise its clause data.
    
    ### Guidelines:
    - A clause may begin with:
    - A number/letter (e.g. "1.", "A."),
    - The word "Clause" followed by a number (e.g. "Clause 1", "Clause 5"), OR
    - An ALL CAPS heading (e.g. "DEFINATION", "TRANSFER OF DATA".)
    
    -Each extracted clause must include:
    -**clause_id** (the exact numbering/label from the contract e.g. "1.", "A.", "Clause 1", "EXHIBIT A" etc)
    -**heading/title** (use the explicit heading if present; if absent, use the first few words of the clause as a makeshift title)
    -**summarised text** (short and summarise text of the clause, including any sub-clauses, preserving legal wording exactly as in the contract, contains only important information from the clause and its sub-clauses)
    
    -Maintain clause boundaries percisly. do not merge multiple clauses into one.
    -Include clauses from exhibits, appendices, and annexes if present.
    -Do not omit any content unless it is clearly not-contractual (e.g. page numbers, headers, footers, blank sihnature lines).
    -response in **valid json** only (no explanation, no notes, no extra text).
    
    Input: {text}
    
    Response in this JSON Structure:
    [
        {{
            "clause_id": "<clause_id>",
            "heading/title": "<heading_or_title>",
            "summarised_text": "<summarised_text__of_clause>"
        }},
        ...
    ]
    """
    response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking
                response_mime_type="application/json",
                response_schema=list[ClauseExtraction],
            ),
            
        )
    response= response.text
    if agreement_type:
        filename_map = {
            "Data Processing Agreement": "jsonFiles/dpa.json",
            "Joint Controller Agreement": "jsonFiles/c2c.json",
            "Controller-to-Controller Agreement": "jsonFiles/jca.json",
            "Processor-to-Subprocessor Agreement": "jsonFiles/scc.json",
            "Standard Contractual Clauses": "jsonFiles/subprocessor.json"
        }
        output_file = filename_map.get(agreement_type)
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(response, f, indent=2, ensure_ascii=False)
            print(f"Saved clause summary to {output_file}")
    
    return response 


if __name__ == "__main__":
    
    try:
        # tamplets mapping 
        TEMPLATE_MAP={
            "dpa.json":"Samples/templates/GDPR-Sample-Agreement.pdf",
            "jca.json":"Samples/templates/(JCA) model-joint-controllership-agreement.pdf",
            "c2c.json":"Samples/templates/(C2C) 2-Controller-to-controller-data-privacy-addendum.pdf",
            "scc.json":"Samples/templates/standard-contractual-clauses.pdf",
            "subprocessing.json":"Samples/templates/(Subprocessing Contract) Personal-Data-Sub-Processor-Agreement-2024-01-24.pdf"
        }
        
        for key, value in TEMPLATE_MAP.items():
            
            response = Clause_extraction(value)
            
            # for summarised flow 
            # response = Clause_extraction_with_summarization("GDPR-Sample-Agreement.pdf")
            
            with open("jsonFiles/"+key, "w", encoding="utf-8") as f:
                json.dump(response, f, indent=2, ensure_ascii=False)
                print(f"Saved clause data to jsonFiles/{key}")
    except Exception as e:
        print("Error Occured",e)
        # notification.send_notification("Error Occured in Template Data Extraction", f"Error is {e}")
        notification.slack_notification(f"Error Occured in Template Data Extraction, Error is {e}")



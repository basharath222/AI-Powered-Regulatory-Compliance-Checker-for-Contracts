from google import genai
from google.genai import types
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from enum import Enum
import PyPDF2
import json
import os

from groq import Groq

# question= "what kind of document is this ?"
# answer= "This is a Data Processing Agreement"

load_dotenv()

# ********   Phase 2    ******** #
def document_type(file):
    
    try:
        class DocumentType(str, Enum):
            DPA= "Data Processing Agreement"
            JCA= "Joint Controller Agreement"
            C2C= "Controller-to-Controller Agreement"
            subprocessor= "Processor-to-Subprocessor Agreement"
            SCC= "Standard Contractual Clauses"
            not_found= "Document type not found"
        
        class FindDocumentType(BaseModel):
            document_type: DocumentType
            
            
        text=""
        with open(file, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
                
        client = genai.Client(api_key=os.getenv("gemini_api_key"))
        
        prompt=f"""
            Tell me what type of document is this
            
            document should be type of between 
            
            1. Data Processing Agreement
            2. Joint Controller Agreement
            3. Controller-to-Controller Agreement
            4. Processor-to-Subprocessor Agreement
            5. Standard Contractual Clauses
            
            Input: {text}
            
            Response in this JSON Structure:
            [{{
                "document_type": "<type_of_document>"
            }},
            ]

        """
        
        response = client.models.generate_content(
            model ="gemini-2.5-flash", contents=prompt,
            # config={
            #     "response_mime_type":"application/json",
            #     "response_schema": list[FindDocumentType],
            # }
            config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking
                    response_mime_type="application/json",
                    response_schema=list[FindDocumentType],
                ),
            )
        json_object = json.loads(response.text)
        # print(json_object[0]['document_type'])
        return json_object[0]['document_type']
    
    except Exception as e:
        print("here for groq api call document type")
        client_groq = Groq(
            api_key=os.environ.get("groq_api_key"),
        )
        chat_completion = client_groq.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
                ],
                model="llama-3.3-70b-versatile",
        )
        print(chat_completion.choices[0].message.content)
        data=chat_completion.choices[0].message.content
        
        
        import re


        if isinstance(data, str):
            data = json.loads(data)


        # Extract document name
        doc_type = data[0]["document_type"]
        
        # regex to remove leading numbers and dots
        doc_name = re.sub(r"^\d+\.\s*", "", doc_type)
        print(doc_name)
            
        return doc_name
        



def compare_agreements(unseen_data, template_data):

    try:
        client = genai.Client(api_key=os.getenv("gemini_api_key2"))
        
        
        prompt=f"""
        You are an AI legal assistant specialized in contract review and compliance.

        Compare the two documents below:

        Template document (regulatory standard reference): 
        {template_data}

        New contract document to review:
        {unseen_data}

        Tasks:
        1. Identify any missing or altered clauses in the new contract compared to the template.
        2. Flag potential compliance risks based on GDPR regulations.
        3. Assign a risk score between 0 and 100 for the new contract (0 = no risk, 100 = maximum risk).
        4. Provide reasoning for the assigned risk score.
        5. Suggest specific amendments or recommendations to bring the contract in line with current regulatory standards and best practices.
        6. Provide the response in a **concise, structured format**, like this:

        - Missing Clauses: [...]
        - Potential Compliance Risks: [...]
        - Risk Score (0-100): ...
        - Reasoning: [...]
        - Recommendations: [...]

        Keep each section brief and focused on key points. Avoid long paragraphs, duplications or unnecessary details.

        """
        
        response = client.models.generate_content(
            model ="gemini-2.5-flash", contents=prompt,
            config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking
                    temperature=0.3
                ),
            )
        
        # print(response.text)
        print("Comparison Completed!!!")
        return response.text
    except Exception as e:
        client_groq = Groq(
            api_key=os.environ.get("groq_api_key"),
        )
        chat_completion = client_groq.chat.completions.create(
        messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
                ],
                model="llama-3.3-70b-versatile",
        )
        # print(chat_completion.choices[0].message.content)
        response=chat_completion.choices[0].message.content
        return response


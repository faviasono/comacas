PROMPT_DOCUMENT = """Try to extract the following information (if available) from a document transcribed:
1.First name 
2.Last & Middle name  
3.Date of Birth 
4.Expiry Date 
5.Document ID
6.Country
7.Gender 

Here the text: 
{document}

Return the results a JSON in the following format.
{
    "first_name": "string",
    "last_name": "string",
    "date_of_birth": "YYYY-MM-DD",
    "expiry_date": "YYYY-MM-DD",
    "document_id": "string",
    "country": "string",
    "gender": "F or M"
}"""
                  
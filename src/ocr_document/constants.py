PROMPT_DOCUMENT = """Try to extract the following information (if available) from a document transcribed:
1.First name 
2.Last & Middle name  
3.Date of Birth 
4.Expiry Date 
5.Document ID
6.Document type (Passport or identity card)
7.Country (Translate it into italian)
8.Nationality (Translate it into italian)
9.Gender 

Here the text: 
##############
{document}
##############

Return the results a JSON in the following format.
{
    "first_name": "string",
    "last_name": "string",
    "date_of_birth": "YYYY-MM-DD",
    "expiry_date": "YYYY-MM-DD",
    "document_id": "string",
    "document_type": "string",
    "country": "string "
    "nationality": "string",
    "gender": "F or M"
}
"""

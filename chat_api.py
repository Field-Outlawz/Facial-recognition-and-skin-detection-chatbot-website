import google.generativeai as genai 

# Configure the API key
genai.configure(api_key="AIzaSyA1G8drq6V7H2Wsm549KU-8Rz2F2RSHln4")
model = genai.GenerativeModel("gemini-1.5-flash")

def message(prompt):
    print("Sending to gemini now")
    response = model.generate_content(prompt)
    print(response)
    return response.text
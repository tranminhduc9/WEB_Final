from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
apikey = "AIzaSyBwGc5TQ14IpygA8FeJaKdGoIFC2sM238k"
client = genai.Client(api_key=apikey)

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)
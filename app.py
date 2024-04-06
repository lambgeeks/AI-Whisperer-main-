from flask import Flask, render_template, request, jsonify
import openai
import speech_recognition as sr
from googletrans import Translator
import spacy
import httpcore
setattr(httpcore, 'SyncHTTPTransport')

# Set your OpenAI API key
openai.api_key = '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'

# Load English tokenizer, tagger, parser and NER
nlp = spacy.load("en_core_web_sm")

# Initialize recognizer class (for recognizing the speech)
r = sr.Recognizer()

app = Flask(__name__)

# Function to extract keywords from text using spaCy
def extract_keywords(text):
    doc = nlp(text)
    keywords = [token.text for token in doc if not token.is_stop and token.pos_ in ['NOUN', 'PROPN', 'ADJ']]
    return keywords

# Function to process speech input
def process_speech(audio_text):
    try:
        # Translate the text to English
        translator = Translator()
        translated_text = translator.translate(audio_text, src='auto', dest='en').text
        
        # Extract keywords from the translated text
        keywords = extract_keywords(translated_text)
        
        # Prepare the text for input to GPT-3.5 model
        messages = [{"role": "system", "content": "You are an intelligent assistant."}]
        
        # Convert translated text to string and add to messages
        translated_str = str(translated_text)
        messages.append({"role": "user", "content": translated_str})
        
        # Send the text to the OpenAI API for chat completion
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
        
        # Get the response from the OpenAI API
        reply = chat.choices[0].message.content
        
        return reply
    
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process-speech', methods=['POST'])
def handle_process_speech():
    data = request.json
    audio_text = data['audio_text']
    reply = process_speech(audio_text)
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True)

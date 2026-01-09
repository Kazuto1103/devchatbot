import requests
import json
import sys
from pprint import pprint

# API Configuration
API_URL = "http://localhost:5000/api/chat"
API_KEY = "sk-dev-ea643c21"

def print_debug_info(response, question):
    """Print detailed debugging information"""
    print("\n" + "="*80)
    print(f"DEBUG INFO - Question: {question}")
    print("-"*40)
    print(f"Status Code: {response.status_code}")
    print("\nResponse Headers:")
    pprint(dict(response.headers))
    
    try:
        print("\nResponse JSON:")
        pprint(response.json())
    except ValueError:
        print("\nResponse Text:")
        print(response.text)
    
    print("="*80 + "\n")

def test_response(question):
    """Test the chatbot with a question and print the response"""
    headers = {"Content-Type": "application/json"}
    data = {
        "apiKey": API_KEY,
        "message": question,
        "stream": False,
        "history": []
    }
    
    try:
        print(f"\nSending request for: {question}")
        response = requests.post(API_URL, json=data, headers=headers, timeout=10)
        
        # Always print debug info for error analysis
        print_debug_info(response, question)
        
        response.raise_for_status()
        result = response.json()
        
        if 'text' in result:
            print(f"\n{'='*80}")
            print(f"QUESTION: {question}")
            print(f"STATUS: {response.status_code}")
            print(f"TOKENS: {len(result['text'].split())} words")
            print("-"*40)
            print(f"RESPONSE: {result['text']}")
            print(f"{'='*80}\n")
        else:
            print("Unexpected response format. Full response:")
            pprint(result)
            
    except requests.exceptions.RequestException as e:
        print(f"\nRequest failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            try:
                print(f"Response: {e.response.json()}")
            except:
                print(f"Response Text: {e.response.text}")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        print(f"Error Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

# Test different question types
test_questions = [
    "Di mana alamat Diskominfo pangkal pinang?",
    "Jam buka kantor kelurahan?",
    "Apa saja syarat membuat KTP?",
    "Bagaimana cara mengurus surat nikah?",
    "Apa itu Kartu Indonesia Pintar?"
]

if __name__ == "__main__":
    print("Testing optimized chatbot responses...\n")
    
    for question in test_questions:
        test_response(question)
        input("Press Enter to test the next question...")
    
    print("All tests completed!")

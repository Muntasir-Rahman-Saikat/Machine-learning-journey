import requests
import json
import os


ROOT_API = "https://muntasir6186-myabsaservice.hf.space"


def call_greets_json():
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(ROOT_API + "/greet", json={}, headers=headers)
        response.raise_for_status()
        result = response.json()
        return {
            "status": "success",
            "response": result,
            "message": "Endpoint is working correctly"
        }

    except requests.exceptions.HTTPError as http_err:
        return {
            "status": "error",
            "error": f"HTTP error occurred: {str(http_err)}",
            "status_code": response.status_code
        }
    except requests.exceptions.RequestException as req_err:
        return {
            "status": "error",
            "error": f"Request error occurred: {str(req_err)}"
        }
    except json.JSONDecodeError:
        return {
            "status": "error",
            "error": "Invalid JSON response from API"
        }


def call_predict_api(text: str, aspect: str) -> dict:
    payload = {
        "text": text,
        "aspect": aspect
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(ROOT_API + "/predict", json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return {
            "status": "success",
            "sentiment": result.get("sentiment"),
            "probabilities": result.get("probabilities"),
            "raw_response": result
        }
    except requests.exceptions.HTTPError as http_err:
        return {
            "status": "error",
            "error": f"HTTP error occurred: {str(http_err)}",
            "status_code": response.status_code
        }
    except requests.exceptions.RequestException as req_err:
        return {
            "status": "error",
            "error": f"Request error occurred: {str(req_err)}"
        }
    except json.JSONDecodeError:
        return {
            "status": "error",
            "error": "Invalid JSON response from API",
            "raw_response": response.text
        }


if __name__ == "__main__":
    # response = call_greets_json()
    # print(response)
    test_cases = [
        {"text": "The food was great but the service was slow", "aspect": "food"},
        {"text": "The ambiance is nice but very crowded", "aspect": "ambiance"}
    ]
    for case in test_cases:
        result = call_predict_api(case["text"], case["aspect"])
        print(f"\nInput: text='{case['text']}', aspect='{case['aspect']}'")
        if result["status"] == "success":
            print(f"Sentiment: {result['sentiment']}")
            print(f"Probabilities: {result['probabilities']}")
        else:
            print(f"Error: {result['error']}")
            if "status_code" in result:
                print(f"Status Code: {result['status_code']}")
            if "raw_response" in result:
                print(f"Raw Response: {result['raw_response']}")
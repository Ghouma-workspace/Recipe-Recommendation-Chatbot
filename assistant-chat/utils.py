import json

def parse_json_response(response):
    """
    Safely parse JSON response from LLM.
    """
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return None

import argparse
import json
from workflow import predict_custom_agent_answer

def main():
    parser = argparse.ArgumentParser(description="Chatbot CLI")
    parser.add_argument("input", type=str, help="User's question")
    args = parser.parse_args()

    try:
        result = predict_custom_agent_answer({"input": args.input})
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))

if __name__ == "__main__":
    main()

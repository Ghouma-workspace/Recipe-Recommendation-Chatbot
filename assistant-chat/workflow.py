import json
import uuid
from langgraph.graph import END, START, StateGraph
from langchain.prompts import PromptTemplate
from typing_extensions import List, TypedDict
from retrieval import retriever
from grading import grade_documents
from models import groq_chat
from langchain_core.output_parsers import StrOutputParser

# Define a typed dict for the state
class GraphState(TypedDict):
    question: str
    generation: str
    decision: str
    search: str
    documents: List
    steps: List[str]

# Define the prompt for generating answers
GROQ_PROMPT = '''You are an AI assistant. Given a question and a set of documents containing relevant information, extract and organize the details clearly and concisely.
Format the answer in a visually appealing manner with appropriate sections such as title, ingredients, and steps.
Question : {question}
Documents : {documents}
'''

prompt_template = PromptTemplate(input_variables=["question", "documents"],
                                 template=GROQ_PROMPT)
rag_chain = prompt_template | groq_chat | StrOutputParser()

def decide_retrieval(state: dict) -> dict:
    """
    Decide whether to retrieve a specific recipe or find recipes based on ingredients.
    """
    question = state["question"]
    decision_prompt = PromptTemplate.from_template(
        """You are an AI assistant that helps users with recipes.
        Given the user's question: "{question}", classify it into one of two categories:
        - "retrieve_recipe": if the user is asking about a specific recipe (e.g., "How do I make a chocolate cake?")
        - "find_recipes": if the user is listing ingredients and asking what they can make (e.g., "What can I prepare with flour and eggs?")

        Respond with only one of these categories in JSON format: {{"decision": "<category>"}}.
        """
    )
    decision_chain = decision_prompt | groq_chat
    decision = decision_chain.invoke({"question": question})
    decision = json.loads(decision.content)
    state["steps"].append("decide_retrieval")
    state["decision"] = decision["decision"]
    return state

def retrieve(state: dict) -> dict:
    """
    Retrieve documents for a specific recipe.
    """
    question = state["question"]
    documents = retriever(question)
    state["steps"].append("retrieve_documents")
    state["documents"] = documents
    return state

def find_recipes(state: dict) -> dict:
    """
    Find recipes based on provided ingredients.
    """
    ingredients = state["question"]
    documents = retriever(ingredients, k=3)
    state["steps"].append("find_recipes")
    state["documents"] = documents
    return state

def generate(state: dict) -> dict:
    """
    Generate answer based on the retrieved documents.
    """
    question = state["question"]
    documents = state["documents"]
    state["steps"].append("generate_answer")
    generation = rag_chain.invoke({"question": question, "documents": documents})
    state["generation"] = generation
    return state

def web_search(state: dict) -> dict:
    """
    Perform web search to supplement documents.
    """
    from langchain_community.tools.tavily_search import TavilySearchResults
    from langchain.schema import Document
    web_search_tool = TavilySearchResults()
    
    question = state["question"]
    state["steps"].append("web_search")
    web_results = web_search_tool.invoke({"query": question})
    
    additional_docs = [
        Document(page_content=d["content"], metadata={"url": d["url"]})
        for d in web_results
    ]
    state["documents"].extend(additional_docs)
    return state

def decide_to_generate(state: dict) -> str:
    """
    Decide whether to run a web search or directly generate the answer.
    """
    if state.get("search") == "Yes":
        return "search"
    return "generate"

def create_workflow():
    workflow = StateGraph(GraphState)

    # Add nodes with their functions
    workflow.add_node("decide_retrieval", decide_retrieval)
    workflow.add_node("find_recipes", find_recipes)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("grade_documents", grade_documents)
    workflow.add_node("generate", generate)
    workflow.add_node("web_search", web_search)

    # Build the graph by setting the entry point and edges
    workflow.set_entry_point("decide_retrieval")
    workflow.add_conditional_edges(
        "decide_retrieval",
        lambda state: state["decision"],
        {"retrieve_recipe": "retrieve", "find_recipes": "find_recipes"},
    )
    workflow.add_edge("find_recipes", "generate")
    workflow.add_edge("retrieve", "grade_documents")
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {"search": "web_search", "generate": "generate"},
    )
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("generate", END)

    custom_graph = workflow.compile()
    return custom_graph

# Function to predict an answer from the custom agent
def predict_custom_agent_answer(example: dict) -> dict:
    import uuid
    custom_graph = create_workflow()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    state_dict = custom_graph.invoke({"question": example["input"], "steps": []}, config)
    return {"response": state_dict["generation"], "steps": state_dict["steps"]}

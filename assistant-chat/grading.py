# grading.py
import json
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from models import groq_chat

# Define the prompt for grading document relevance
GRADE_PROMPT = PromptTemplate(
    template="""You are a strict grader assessing the relevance of a retrieved document to a user question. \n
    Here is the retrieved document: \n\n {document} \n\n
    Here is the user question: {question} \n
    A document is considered relevant **only** if it contains **exact** keywords from the user question or **closely related synonyms**. \n
    If the document lacks these key terms, or if the content is only loosely related, it must be graded as **irrelevant**. \n
    Err on the side of **marking documents as irrelevant** unless they clearly match the user's request. \n
    Be highly conservative in marking a document as relevant—assume it is irrelevant unless there is clear evidence of a match. \n
    Provide the binary score as a JSON with a single key 'score' and no premable or explanation.
    JSON format is as follows: {{"score": "yes/no"}}
    """,
    input_variables=["question", "document"],
)

retrieval_grader = GRADE_PROMPT | groq_chat | JsonOutputParser()

def grade_documents(state: dict) -> dict:
    """
    Determines whether the retrieved documents are relevant to the question.
    """
    question = state["question"]
    documents = state["documents"]
    steps = state["steps"]
    steps.append("grade_document_retrieval")
    filtered_docs = []
    search = "No"
    for d in documents:
        # Assume d has a field 'page_content'
        score = retrieval_grader.invoke({"question": question, "document": d.page_content})
        grade = score["score"]
        if grade == "yes":
            filtered_docs.append(d)
        else:
            search = "Yes"
    state.update({"documents": filtered_docs, "search": search, "steps": steps})
    return state

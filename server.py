from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from fastapi import FastAPI
% % writefile server.py


def llm(port):
    return ChatOpenAI(
        base_url=f"http://localhost:{port}/v1",
        api_key="EMPTY",
        model="local"
    )


planner = llm(8003)
coder = llm(8001)
review = llm(8002)


class State(dict):
    pass


graph = StateGraph(State)


def plan(s):
    s["plan"] = planner.invoke(s["input"]).content
    return s


def code(s):
    s["code"] = coder.invoke(s["plan"]).content
    return s


def check(s):
    s["review"] = review.invoke(s["code"]).content
    return s


graph.add_node("plan", plan)
graph.add_node("code", code)
graph.add_node("review", check)
graph.set_entry_point("plan")
graph.add_edge("plan", "code")
graph.add_edge("code", "review")

app_graph = graph.compile()

app = FastAPI()


@app.post("/chat")
def chat(prompt: str):
    return app_graph.invoke({"input": prompt})

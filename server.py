from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import TypedDict
from pydantic import BaseModel

print("### BACKEND VERSION: TypedDict State ###")


def llm(port):
    return ChatOpenAI(
        base_url=f"http://localhost:{port}/v1",
        api_key="EMPTY",
        model="Qwen/Qwen2.5-3B-Instruct",
        temperature=0.2,
    )


planner = llm(8003)
coder = llm(8003)
review = llm(8003)


class State(TypedDict, total=False):
    input: str
    plan: str
    code: str
    review: str


def plan(s: State) -> State:
    s["plan"] = planner.invoke(s["input"]).content
    return s


def code(s: State) -> State:
    s["code"] = coder.invoke(s["plan"]).content
    return s


def check(s: State) -> State:
    s["review"] = review.invoke(s["code"]).content
    return s


graph = StateGraph(State)

graph.add_node("plan", plan)
graph.add_node("code", code)
graph.add_node("review", check)

graph.add_edge(START, "plan")
graph.add_edge("plan", "code")
graph.add_edge("code", "review")
graph.add_edge("review", END)

app_graph = graph.compile()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    prompt: str


@app.post("/chat")
def chat(req: ChatRequest):
    return app_graph.invoke({"input": req.prompt})


@app.get("/prompt")
def prompt_test():
    return app_graph.invoke({"input": "hi"})


@app.get("/health")
def health():
    return {"ok": True, "version": "typed-dict-state"}

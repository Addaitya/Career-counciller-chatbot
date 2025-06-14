from typing import TypedDict, Annotated
from langchain_core.prompts import ChatPromptTemplate
from utils import get_llm, get_prompts
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_core.messages.tool import ToolMessage
from langchain_core.messages.human import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt.tool_node import ToolNode
from langchain_core.tools import tool

prompts = get_prompts()
def get_career_recommendation(conversation: str):
    llm = get_llm()
    career_prompt_template = prompts.get('career_recommendation', "")
    career_prompt= career_prompt_template.format(conversation=conversation)
    response = llm.invoke(
        [('human', career_prompt)]
    )

    return response


class State(TypedDict):
    messages: Annotated[list, add_messages]
    clarification_needed: bool
    question: str

@tool
def add_clarification(question: str):
    '''
    Ask student clarification question.
    '''
    return question

def clarification_checker_assistant(state: State):
    clarification_prompt_template = prompts.get("ask_clarifying_question", "")
    clarification_prompt = ChatPromptTemplate(
        [
            ('system', clarification_prompt_template),
            ('placeholder', "{messages}")
        ]
    )

    llm = get_llm()
    llm_with_tools = llm.bind_tools([add_clarification])
    runnable = clarification_prompt | llm_with_tools
    response = runnable.invoke(state)

    clarification_needed = False
    if hasattr(response, 'tool_calls') and len(response.tool_calls) > 0:
        clarification_needed = True
        return {'messages': [response], 'clarification_needed': clarification_needed}
    return {'clarification_needed': False }

def route_tools(state: State):
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return 'summarise_answers'

def summarise_answers(state: State):
    messages = state['messages']

    human_messages = []
    for message in messages:
        if isinstance(message, HumanMessage):
            human_messages.append(message)
    summary_prompt_template = prompts.get('summarise_answer', "")
    summary_prompt = ChatPromptTemplate(
        [
            ('system', summary_prompt_template),
        ]
    )
    llm = get_llm()

    runnable = summary_prompt | llm

    # print("*"*20, "Conversation", "*"*20)
    # from pprint import pprint
    # pprint(state['messages'])
    # print("*"*20, "*"*20)

    # state['human_messages'] = human_messages
    # response = runnable.invoke(state)
    # print("*"*20, "Summary", "*"*20)
    # print(response)
    # return {"messages": [response]}

builder = StateGraph(State)

builder.add_edge(START, 'ask_clarification')
builder.add_node('ask_clarification', clarification_checker_assistant)
builder.add_node('summarise_answers', summarise_answers)
builder.add_node('tools', ToolNode([add_clarification]))
builder.add_conditional_edges('ask_clarification', route_tools, path_map={"tools": "tools", "summarise_answers":"summarise_answers"})
builder.add_edge('tools', END)
builder.add_edge('summarise_answers', END)

checkpointer = InMemorySaver()
clarification_graph = builder.compile(checkpointer=checkpointer)


# import asyncio
# from pprint import pprint

# def execute():
#     config = {"configurable": {"thread_id": "1"}}
#     response = clarification_graph.invoke({"messages": [('ai', "Which school subjects or activities do you enjoy the most and why?"), ('human', 'I enjoy Maths and Science subject because in include problem solving and numbers. These are only subjects i enjoy.')]}, config=config)
#     pprint(response)
# asyncio.run(execute())
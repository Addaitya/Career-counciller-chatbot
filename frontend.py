import streamlit as st
import os

os.environ['LLM_API_KEY'] = st.secrets['LLM_API_KEY']
from agent import get_career_recommendation, clarification_graph

st.title("Career counselling")


if "clarification_needed" not in st.session_state:
    st.session_state.clarification_needed = False

if "curr_ques_id" not in st.session_state:
    st.session_state.curr_ques_id = 0

if "curr_ans" not in st.session_state:
    st.session_state.curr_ans = ""

if "questions" not in st.session_state:
    st.session_state.questions = [
        "Which school subjects do you enjoy the most and why?",
        "Do you prefer solving problems logically, expressing ideas creatively, or engaging in physical activities?",
        'Who inspires you more — a scientist/engineer, an artist/writer, or an athlete?'
    ]

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            'role': "assistant",
            'content': "Hi i am you ai career counselor. Answer following questions to get a career recommendation."
        },
        {
            'role': "assistant",
            'content': st.session_state.questions[st.session_state.curr_ques_id]
        }
    ]

if "answers" not in st.session_state:
    st.session_state.answers = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

@st.dialog("Career Recommendation")
def recommend(item):
        st.markdown(item)

# Side bar
sideb = st.sidebar
Generate_recommendation_btn = sideb.button("Get Recommendations")
if Generate_recommendation_btn:
        if st.session_state.answers:
            response = get_career_recommendation("\n".join(st.session_state.answers))
            recommend(response.content)
        else:
            sideb.markdown("Button Enable after one question is answered properly along with clarification questions.")



if prompt := st.chat_input("Answer questions"):

    
    ## chat interface
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.curr_ans = prompt
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        config = {"configurable": {"thread_id": str(st.session_state.curr_ques_id)}}
        messages = []
        if st.session_state.clarification_needed:
            response = clarification_graph.invoke({"question": st.session_state.questions[st.session_state.curr_ques_id], 'messages': [('human', st.session_state.curr_ans)]}, config)
        else:
            response = clarification_graph.invoke({"question": st.session_state.questions[st.session_state.curr_ques_id],'messages': [('ai', st.session_state.questions[st.session_state.curr_ques_id]), ('human', st.session_state.curr_ans)]}, config)

        if response['clarification_needed']:
            st.session_state.clarification_needed = True
            st.session_state.messages.append({"role": "assistant", "content": "[Clarification Question]: " + response['messages'][-1].content})
            st.markdown("[Clarification Question]: "+response['messages'][-1].content)
        else:
            if st.session_state.curr_ques_id >= len(st.session_state.questions)-1:
                response = get_career_recommendation("\n".join(st.session_state.answers))
                recommend(response.content)
            else:
                st.session_state.clarification_needed = False
                st.session_state.curr_ques_id += 1
                st.session_state.messages.append({"role": "assistant", "content": st.session_state.questions[st.session_state.curr_ques_id]})
                st.session_state.answers.append(response['messages'][-1].content)
                print(response['messages'][-1].content)
                st.markdown(st.session_state.questions[st.session_state.curr_ques_id])
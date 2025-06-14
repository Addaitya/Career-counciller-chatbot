from agent import summarise_answers, clarification_graph

questions = [
"Which school subjects or activities do you enjoy the most and why?",
"Do you prefer solving problems logically, expressing ideas creatively, or engaging in physical activities?",
'What are you naturally good at — numbers and reasoning, creative expression, or physical coordination?',
'Who inspires you more — a scientist/engineer, an artist/writer, or an athlete?'
]

answers = []
def run_app():
    print("AI: Hey there I will ask you some questions")
    for i,question in enumerate(questions):
        print(f'AI: {question}')
        answer = input("You: ")

        config = {"configurable": {"thread_id": str(i)}}
        response = clarification_graph.invoke({'messages': [('ai', question), ('human', answer)]}, config)
        print(f"\nQuestion {i}: {response['clarification_needed']}\n")

        while response['clarification_needed']:
            clarification_question = response['messages'][-1].content
            print(f"AI: {clarification_question}")
            answer = input("You: ")
            response = clarification_graph.invoke({'messages': [('ai', clarification_question), ('human', answer)]}, config)
        answers.append(response['messages'][-1].content)
    
    print()
    print("-*"*50)
    print(answers)


run_app()
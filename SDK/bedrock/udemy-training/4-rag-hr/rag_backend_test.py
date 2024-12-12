import rag_backend_cohere_claude3 as backend 

index = backend.hr_index()
llm = backend.hr_llm()
response_content = backend.hr_rag_response(index=index, question='How many privilege in a year')
print(response_content)
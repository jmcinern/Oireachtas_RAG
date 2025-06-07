# Oireachtas_RAG
- RAG model to query Dáil debates. This is a personal project. I came across the Oireachtas database and API: https://data.oireachtas.ie/ and saw the availibilty of information.
- I am building a RAG model whereby, one can query the model to get TDs positions on issues. This will help voters make informed decisions, allowing them to access primary sources.
- This project has also become an area of interest for research at Trinity College Dublin. 
 
TODO:
- Web app deployment.
- Further refining of prompt engineering, especially in cases where there are few relevant quotes.

Sample: 

- Leo Varadkar on the Housing Crisis 


> Leo Varadkar acknowledges that 'the very real housing crisis we face in this country is a disaster for many people' (2022, https://data.oireachtas.ie/akn/ie/debateRecord/dail/2022-06-16/debate/mul@/main.xml). He emphasizes that 'the causes of the housing crisis are multifactorial' and rejects simplistic explanations or blaming the Opposition (2023, https://data.oireachtas.ie/akn/ie/debateRecord/dail/2023-04-25/debate/mul@/main.xml). Varadkar criticizes objections to housing developments, stating 'we cannot fix the housing crisis without increased supply of all types of housing' (2023, https://data.oireachtas.ie/akn/ie/debateRecord/dail/2023-04-25/debate/mul@/main.xml). Additionally, he notes efforts 'to come up with new and more dramatic language to describe the housing situation' (2023, https://data.oireachtas.ie/akn/ie/debateRecord/dail/2023-03-29/debate/mul@/main.xml).

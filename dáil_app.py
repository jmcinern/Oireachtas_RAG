# requirements.txt
# install requirements.txt from project_fpath + requirements.txt
import subprocess
subprocess.check_call(["python", "-m", "pip", "install", "-qU", "-r", "./requirements.txt"])# list of speakers

# speakers.txt
SPEAKERS = set()
with open("./speakers.txt", "r", encoding="utf-8") as file:
  for line in file:
    name = line.strip()
    SPEAKERS.add(name)

# examples
import json
# examples.json
with open("./dail_examples.json", "r", encoding="utf-8") as f:
    examples = json.load(f)
    
###################################################################################
import os
import json
import boto3
import chromadb                          # Vector DB
import openai                            # model for generation
import streamlit as st                  # Streamlit UI
from thefuzz import process             # for fuzzy speaker lookup
from langchain.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate
)
from langchain_community.chat_models import ChatOpenAI
from thefuzz import process
import spacy
# Load the spaCy model for NLP tasks and cache
nlp = spacy.load("en_core_web_sm")



#st.write("SECRETS DIAGNOSTIC:", st.secrets)

# 1. Load your OpenAI key from Streamlit secrets
#openai.api_key = 

# 2. Download & cache the ChromaDB vector store from S3
@st.cache_resource
def download_debate_db_from_s3(bucket_name: str, s3_prefix: str, local_dir: str) -> str:
    os.makedirs(local_dir, exist_ok=True)

    aws_access_key_id     = st.secrets["aws"]["aws_access_key_id"]
    aws_secret_access_key = st.secrets["aws"]["aws_secret_access_key"]

    s3_resource = boto3.resource(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    bucket = s3_resource.Bucket(bucket_name)

    for obj in bucket.objects.filter(Prefix=s3_prefix):
        key = obj.key
        if key.endswith("/"):
            continue
        rel_path = key[len(s3_prefix) : ]
        local_path = os.path.join(local_dir, rel_path)
        local_subdir = os.path.dirname(local_path)
        if not os.path.exists(local_subdir):
            os.makedirs(local_subdir, exist_ok=True)
        bucket.download_file(Key=key, Filename=local_path)

    return local_dir

debate_db_path = download_debate_db_from_s3(
    bucket_name="joebucketai",
    s3_prefix="debate_db_urls/debate_db/",
    local_dir="D:/tmp/debate_db/"
)
chroma_client = chromadb.PersistentClient(path=debate_db_path)
collection = chroma_client.get_or_create_collection("oireachtas_debates")

# 3. Few-shot prompt setup
example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{question}?"),
    ("ai",    "{answer}\n")
])
few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt
)
full_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an Irish parliament chatbot. Users will ask "
        "about politicians' opinions on topics. You will summarise "
        "their positions using only provided quotes with URL/year citations."
    )),
    few_shot_prompt,
    ("human", "{question}")
])

gpt_nano = ChatOpenAI(
    model_name="gpt-4.1-nano",
    temperature=0.9,
    openai_api_key=st.secrets["openai"]["api_key"]
)
chain_nano = full_prompt | gpt_nano

# 4. Helper functions
def search_speaker_position(speaker_name, topic, num_results=5):
    results = collection.query(
        query_texts=[topic],
        n_results=num_results,
        where={"speaker": speaker_name},
        include=["metadatas"]
    )
    print(results["metadatas"][0])
    if not results["metadatas"][0]:
        return f"No speeches found for {speaker_name} on {topic}."
    out = f"### {speaker_name}'s Position on '{topic}':\n"
    for i, md in enumerate(results["metadatas"][0], 1):
        url = ""
        if "url" in md:
            url  = md["url"]
        text = md["text"][:500].replace("\n", " ")
        out += f"\n**Quote {i} (source: {url}):** {text}...\n"
    return out



def generate_answer(speaker_name, topic, list_of_speakers):
    quotes = search_speaker_position(speaker_name, topic)
    if quotes.startswith("No speeches found"):
        return quotes
    resp = chain_nano.invoke({
        "question": f"Summarise {speaker_name}'s position on {topic} using these quotes: {quotes}",
        "answer": ""
    })
    return resp.content


# 6. Streamlit UI
def main():
    st.title("Dáil Speeches Explorer")
    # get user input
    input = st.text_input("Question", placeholder="What has Leo Varadkar said regarding the housing crisis?")
    if input:
        spacy_doc = nlp(input)
        # extract named entities
        entities = [ent.text for ent in spacy_doc.ents if ent.label_ == "PERSON"]
        speaker_name = "not found"
        for entity in entities:
            # find closest match between SPEAKERS and input
            speaker_name = match_speaker(input, SPEAKERS, 80)
        # not found
        if speaker_name == "not found":
            st.error("Speaker not found. Please check the spelling or try a different name.")
            # print list of speakers
            st.write("Available speakers:")
            st.write(", ".join(sorted(SPEAKERS)))
        # found
        else:
            st.write(f"Summarising for {speaker_name}, please wait...")
            with st.spinner("Generating response..."):
                answer = generate_answer(speaker_name, input, SPEAKERS)
            st.write(answer)
        

    

if __name__ == "__main__":
    main()

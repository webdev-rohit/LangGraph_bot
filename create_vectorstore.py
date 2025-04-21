import pandas as pd
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings

# Load CSV
df = pd.read_csv("ticket_solutions.csv")

# Create documents
documents = [
    Document(page_content=row['solution'], metadata={"user_issue": row['query']})
    for _, row in df.iterrows()
]

# loading openai api key
from dotenv import load_dotenv
import os
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Create ChromaDB vectorstore
embedding = OpenAIEmbeddings(api_key=openai_api_key)

vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embedding,
    persist_directory="./chroma_db"
)

vectorstore.persist()

import os
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.cassandra import Cassandra
from langchain.document_loaders import TextLoader
from langchain.embeddings import HuggingFaceEmbeddings
from PyPDF2 import PdfReader
from langchain.document_loaders import DirectoryLoader
import gzip

database_mode = 'C'  # Hardcoded value for database mode
keyspace_name = 'langch'  # Hardcoded keyspace name

if database_mode == 'C':
    CASSANDRA_CONTACT_POINTS = '172.16.7.11'  # Hardcoded Cassandra contact points

if database_mode == 'C':
    if CASSANDRA_CONTACT_POINTS:
        cluster = Cluster([
            cp.strip()
            for cp in CASSANDRA_CONTACT_POINTS.split(',')
            if cp.strip()
        ])
    else:
        cluster = Cluster()
    session = cluster.connect(keyspace=keyspace_name)

pdf_loader = DirectoryLoader('./data', glob="**/*.txt")

loaders = [pdf_loader]
documents = []
for loader in loaders:
    documents.extend(loader.load())

text_splitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

table_name = 'embedding'
docsearch = Cassandra.from_documents(
    documents=docs,
    embedding=embeddings,
    session=session,
    keyspace=keyspace_name,
    table_name=table_name,
)

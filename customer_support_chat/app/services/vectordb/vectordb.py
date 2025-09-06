# customer_support_chat/app/services/vectordb/vectordb.py
import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from customer_support_chat.app.core.settings import get_settings
from customer_support_chat.app.services.utils import get_qdrant_client
from customer_support_chat.app.services.vectordb.chunkenizer import recursive_character_splitting
from customer_support_chat.app.core.logger import logger
from langchain_openai import OpenAIEmbeddings

settings = get_settings()

class VectorDB:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.client = get_qdrant_client()
        # Initialize OpenAI embeddings
        if settings.OPENAI_BASE_URL:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_BASE_URL
            )
        else:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=settings.OPENAI_API_KEY
            )
        self.create_collection()

    def create_collection(self):
        if not self.client.get_collection(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
            logger.info(f"Created new collection: {self.collection_name}")
        else:
            logger.info(f"Collection {self.collection_name} already exists")

    def generate_embedding(self, content):
        return self.embeddings.embed_query(content)

    def upsert_vector(self, doc_id, chunk_text, embedding, url, chunk_index):
        chunk_id = str(uuid.uuid4())
        payload = {
            "url": url,
            "document_id": str(doc_id),
            "chunk_index": chunk_index,
            "chunk_text": chunk_text,
        }

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(id=chunk_id, vector=embedding, payload=payload)
            ]
        )

    def create_embeddings(self, docs):
        for doc_id, content, url in docs:
            if content is None:
                logger.warning(f"Skipping doc_id {doc_id} because content is None")
                continue

            chunks = recursive_character_splitting(content)
            for i, chunk in enumerate(chunks):
                try:
                    logger.info(f"Generating embedding for doc_id: {doc_id}, chunk: {i+1}")
                    embedding = self.generate_embedding(chunk)
                    self.upsert_vector(doc_id, chunk, embedding, url, i)
                except Exception as e:
                    logger.error(f"Failed to generate or store embedding for doc_id: {doc_id}, chunk: {i+1}, error: {str(e)}")

        logger.info("Completed generating embeddings for all documents")

    def search(self, query, k=3):
        query_embedding = self.generate_embedding(query)
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=k,
            with_payload=True,
        )
        return search_result

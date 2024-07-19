
from organization.models import Document
import numpy as np
from transformers import pipeline

vectorizer = pipeline('feature-extraction', model='bert-base-uncased')

def store_document(name, content, repository):
    vector = np.array(vectorizer(content)).mean(axis=1)
    document = Document.objects.create(
        name=name,
        content=content,
        vector=vector,
        repository=repository
    )
    return document

def query_documents(query, repository):
    query_vector = np.array(vectorizer(query)).mean(axis=1)
    documents = Document.objects.filter(repository=repository).order_by('-vector__cosine_distance', query_vector)
    return documents

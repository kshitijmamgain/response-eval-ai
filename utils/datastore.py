import hnswlib
from typing import List, Dict
from unstructured.partition.text import partition_text
from unstructured.chunking.title import chunk_by_title

class Datastore:
    """
    A class representing a collection of documents.

    Parameters:
    sources (list): A list of dictionaries representing the sources of the documents. Each dictionary should have 'title' and 'url' keys.

    Attributes:
    sources (list): A list of dictionaries representing the sources of the documents.
    docs (list): A list of dictionaries representing the documents, with 'title', 'content', and 'url' keys.
    docs_embs (list): A list of the associated embeddings for the documents.
    docs_len (int): The number of documents in the collection.
    index (hnswlib.Index): The index used for document retrieval.

    Methods:
    load_and_chunk(): Loads the data from the sources and partitions the HTML content into chunks.
    embed(): Embeds the documents using the Cohere API.
    index(): Indexes the documents for efficient retrieval.
    """

    def __init__(self, raw_documents: List[Dict[str, str]]):
        self.raw_documents = raw_documents  # raw documents
        self.chunks = []            # chunked version of documents
        self.chunks_embs = []       # embeddings of chunked documents
        self.retrieve_top_k = 10
        self.rerank_top_k = 3
        self.load_and_chunk()  # load raw documents and break into chunks
        self.embed() # generate embeddings for each chunk
        self.index() # store embeddings in an index


    def load_and_chunk(self) -> None:
        """
        Loads the text from the sources and chunks the HTML content.
        """
        print("Loading documents...")

        for source in self.raw_documents:
            elements = partition_text(filename=source["filename"])
            chunks = chunk_by_title(elements)
            for chunk in chunks:
                self.chunks.append(
                    {
                        "title": source["title"],
                        "text": str(chunk),
                        "url": source["filename"],
                    }
                )

    def embed(self) -> None:
        """
        Embeds the document chunks using the Cohere API.
        """
        print("Embedding document chunks...")

        batch_size = 90
        self.chunks_len = len(self.chunks)

        for i in range(0, self.chunks_len, batch_size):
            batch = self.chunks[i : min(i + batch_size, self.chunks_len)]
            texts = [item["text"] for item in batch]
            chunks_embs_batch = co.embed(
                texts=texts, model="embed-english-v3.0", input_type="search_document"
            ).embeddings
            self.chunks_embs.extend(chunks_embs_batch)

    def index(self) -> None:
        """
        Indexes the document chunks for efficient retrieval.
        """
        print("Indexing documents...")

        self.idx = hnswlib.Index(space="ip", dim=1024)
        self.idx.init_index(max_elements=self.chunks_len, ef_construction=512, M=64)
        self.idx.add_items(self.chunks_embs, list(range(len(self.chunks_embs))))

        print(f"Indexing complete with {self.idx.get_current_count()} documents.")

        return self.idx

    def search_and_rerank(self, query: str) -> List[Dict[str, str]]:
        # SEARCH
        query_emb = co.embed(
                  texts=[query], model="embed-english-v3.0", input_type="search_query"
              ).embeddings

        chunk_ids = self.idx.knn_query(query_emb, k=self.retrieve_top_k)[0][0]

        # RERANK
        chunks_to_rerank = [self.chunks[chunk_id]["text"] for chunk_id in chunk_ids]

        rerank_results = co.rerank(
            query=query,
            documents=chunks_to_rerank,
            top_n=self.rerank_top_k,
            model="rerank-english-v2.0",
        )

        chunk_ids_reranked = [chunk_ids[result.index] for result in rerank_results]

        chunks_retrieved = []
        for chunk_id in chunk_ids_reranked:
            chunks_retrieved.append(
                {
                "title": self.chunks[chunk_id]["title"],
                "text": self.chunks[chunk_id]["text"],
                "filename": self.chunks[chunk_id]["url"],
                }
            )

        return chunks_retrieved
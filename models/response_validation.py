import os
import cohere
import uuid
from utils.datastore import Datastore
from utils.model_guardrails import guard

from dotenv import load_dotenv
load_dotenv()
COHERE_API_KEY=os.getenv('COHERE_API_KEY')
co = cohere.Client(COHERE_API_KEY)

class ResponseEvalAI:
    def __init__(self, datastore: Datastore):
        """
        Initializes an instance of the Chatbot class.

        Parameters:
        storage (Storage): An instance of the Storage class.

        """
        self.datastore = datastore
        self.conversation_id = str(uuid.uuid4())
        self.response_queries = None
        self.chunks = []
        self.documents = []

    def _get_reranked_docs(self, prompt):
            self.response_queries = co.chat(message=prompt, search_queries_only=True)

            if self.response_queries.search_queries:
                print("Retrieving information...", end="")

                # Get the query(s)
                queries = []
                for search_query in self.response_queries.search_queries:
                    queries.append(search_query["text"])

                # Retrieve documents for each query
                for query in queries:
                    self.chunks.extend(self.datastore.search_and_rerank(query))
            
            else:
                print('unable to locate the information')
                
        
    def run(self, prompt, **kwargs):
        """
        Runs the chatbot application.

        """
        self._get_reranked_docs(prompt)
        while True:
            # Get the user message

            response = co.chat(
                message=prompt,
                # model='command-nightly',
                documents=self.chunks,
                conversation_id=self.conversation_id, 
                **kwargs
                # stream=True,
                # temperature=0.2
                )

            # Documents
            if response.citations:
                print("\n\nDOCUMENTS:")
                self.documents = [{'id': doc['id'],
                                'text': doc['text'][:50] + '...',
                                'title': doc['title'],
                                'url': doc['filename']} 
                                for doc in response.documents]

            return response.text
        
def response_evaluator(question, answer):
    sources = [
    {
        "title": "Data Quarkle", 
        "filename": "sample-docs/concept-dataquarkle.md"},
    {
        "title": "RAGs", 
        "filename": "sample-docs/undestanding-rags.md"},
        {
        "title": "sample", 
        "filename": "sample-docs/sample.md"},    
        {
        "title": "de-concepts", 
        "filename": "sample-docs/understanding-de-concepts.md"}, 
]

# Create an instance of the Datastore class with the given sources
    datastore = Datastore(sources, co)
    
    _response = ResponseEvalAI(datastore)
    expected_answer = _response.run(prompt=question, temperature=0.1)

    evaluate_response = guard(_response.run,
                model='command-nightly',
                prompt_params={'question':question, 'answer': answer, 'expected_answer':expected_answer},
                temperature=0.3
                )
    assessment=evaluate_response.validated_output
    return assessment
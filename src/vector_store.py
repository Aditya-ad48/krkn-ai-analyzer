import os
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


class ExperimentMemory:
    """
    Stores experiment summaries and allows semantic comparison.
    """

    def __init__(self, persist_dir=None):
        self.persist_dir = persist_dir or os.getenv("CHROMA_DB_DIR", ".chroma")
        self.db = Chroma(
            collection_name="krkn_experiments",
            persist_directory=self.persist_dir
        )

    def store_experiment(self, experiment_id: str, text: str, metadata: dict):
        doc = Document(page_content=text, metadata=metadata)
        self.db.add_documents([doc], ids=[experiment_id])
        self.db.persist()

    def semantic_search(self, query: str, k: int = 5):
        return self.db.similarity_search(query, k=k)

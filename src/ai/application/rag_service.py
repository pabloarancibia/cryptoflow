from typing import List
from src.ai.domain.ports import IVectorStore, ILLMProvider
from src.ai.domain.models import DocumentChunk

class RAGService:
    def __init__(self, vector_store: IVectorStore, llm_provider: ILLMProvider):
        self.vector_store = vector_store
        self.llm_provider = llm_provider

    def answer_question(self, query: str) -> str:
        # 1. HyDE: Generate hypothetical answer
        print(f"RAG: generating HyDE for '{query}'...")
        hyde_prompt = f"Write a short, hypothetical technical paragraph from the documentation that answers: {query}. Focus on technical terminology and system architecture."
        hyde_doc = self.llm_provider.generate_text(hyde_prompt, system_instruction="You are an expert technical writer.")
        
        # 2. Retrieve relevant docs using HyDE doc
        print("RAG: retrieving documents...")
        relevant_docs = self.vector_store.query(hyde_doc, n_results=5)
        
        if not relevant_docs:
            return "I couldn't find any relevant documentation to answer your question."

        # 3. Build Context
        context_str = "\n\n".join([f"Source: {d.metadata.get('source', 'unknown')}\n{d.content}" for d in relevant_docs])
        
        # 4. Generate Final Answer
        print("RAG: generating final answer...")
        final_prompt = f"""Based on the following context, answer the user's question.

Context:
{context_str}

Question: {query}
"""
        answer = self.llm_provider.generate_text(final_prompt, system_instruction="You are a helpful assistant for the CryptoFlow platform.")
        return answer

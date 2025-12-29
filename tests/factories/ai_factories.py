from faker import Faker

fake = Faker()

class DocumentChunkFactory:
    """Factory to generate dummy document chunks and metadata."""
    
    @staticmethod
    def create_chunk(file_path=None, chunk_index=0):
        if not file_path:
            file_path = f"docs/{fake.word()}.md"
        
        content = fake.paragraph(nb_sentences=5)
        return {
            "document": content,
            "metadata": {"source": file_path},
            "id": f"{file_path}_{chunk_index}"
        }

    @staticmethod
    def create_batch(size=3):
        return [DocumentChunkFactory.create_chunk(chunk_index=i) for i in range(size)]

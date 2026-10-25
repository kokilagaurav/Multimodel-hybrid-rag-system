from langchain_community.document_loaders import PyMuPDFLoader

class PDFLoader:
    def __init__(self):
        pass
    def load_pdf(self, file_path):
        loader = PyMuPDFLoader(
            file_path,
            extract_images=True,          # Extracts embedded images
            extract_tables="markdown",
        )

        document = loader.load()

        return document

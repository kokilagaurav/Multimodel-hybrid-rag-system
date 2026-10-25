from langchain_community.document_loaders import TextLoader

class text_loader:
    def __init__(self):
        pass

    def load_text(self, file_path):
        loader = TextLoader(
            file_path,
            encoding = "utf-8"
        )

        documents = loader.load()

        return documents
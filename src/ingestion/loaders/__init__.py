"""Document loaders."""

from src.ingestion.loaders.csv_loader import CSVLoader
from src.ingestion.loaders.json_loader import JSONLoader
from src.ingestion.loaders.markdown_loader import MarkdownLoader
from src.ingestion.loaders.pdf_loader import PDFLoader
from src.ingestion.loaders.text_loader import TextLoader

DEFAULT_LOADERS = [MarkdownLoader(), TextLoader(), PDFLoader(), JSONLoader(), CSVLoader()]

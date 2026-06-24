"""PDF table extraction helpers."""

from pathlib import Path


class TableExtractor:
    def extract_tables(self, pdf_path: Path) -> list[str]:
        tables: list[str] = []
        try:
            import camelot

            parsed = camelot.read_pdf(str(pdf_path), pages="all")
            for idx, table in enumerate(parsed, start=1):
                tables.append(f"Table {idx}\n{table.df.to_csv(index=False)}")
        except Exception:
            return []
        return tables

"""CAS (Consolidated Account Statement) PDF parser for CDSL/NSDL statements."""

import logging
import re
from io import BytesIO

import pdfplumber

from app.brokers.base import BrokerHolding, PdfParser
from app.brokers.isin_map import resolve_isin

logger = logging.getLogger(__name__)

# ISIN pattern: INE followed by 9 alphanumeric characters
ISIN_RE = re.compile(r"\b(INE[A-Z0-9]{9})\b")


class CasPdfParser(PdfParser):
    name: str = "cdsl_nsdl"
    display_name: str = "CDSL/NSDL CAS (PDF)"

    def parse_pdf(self, content: bytes) -> list[BrokerHolding]:
        """Parse a CDSL/NSDL CAS PDF and extract holdings.

        CAS PDFs vary in format but generally contain:
        - ISIN code (INExxxxxxxxx)
        - Security/company name (near the ISIN)
        - Quantity/balance (numeric value)
        """
        holdings: list[BrokerHolding] = []
        seen_isins: set[str] = set()

        with pdfplumber.open(BytesIO(content)) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Try table extraction first
                tables = page.extract_tables() or []
                for table in tables:
                    holdings.extend(
                        self._parse_table_rows(table, seen_isins)
                    )

                # Also scan raw text for ISINs not captured in tables
                text = page.extract_text() or ""
                holdings.extend(
                    self._parse_text_lines(text, seen_isins)
                )

        if not holdings:
            raise ValueError(
                "No holdings found in PDF. Please ensure this is a valid "
                "CDSL/NSDL CAS (Consolidated Account Statement)."
            )

        logger.info("Parsed %d holdings from CAS PDF", len(holdings))
        return holdings

    def _parse_table_rows(
        self, table: list[list[str | None]], seen_isins: set[str]
    ) -> list[BrokerHolding]:
        """Extract holdings from a PDF table."""
        results: list[BrokerHolding] = []

        for row in table:
            if not row:
                continue

            # Join all cells to search for ISIN
            row_text = " ".join(cell or "" for cell in row)
            isin_match = ISIN_RE.search(row_text)
            if not isin_match:
                continue

            isin = isin_match.group(1)
            if isin in seen_isins:
                continue

            # Extract company name: text before or around the ISIN
            company_name = self._extract_company_name(row, row_text, isin)

            # Extract quantity: look for numeric values in the row
            quantity = self._extract_quantity(row)
            if quantity is None or quantity <= 0:
                continue

            symbol = resolve_isin(isin, company_name)
            if not symbol:
                logger.warning(
                    "Skipping unresolvable ISIN %s (%s)", isin, company_name
                )
                continue

            seen_isins.add(isin)
            results.append(
                BrokerHolding(
                    symbol=symbol,
                    quantity=quantity,
                    avg_buy_price=0.0,
                    current_price=0.0,
                )
            )

        return results

    def _parse_text_lines(
        self, text: str, seen_isins: set[str]
    ) -> list[BrokerHolding]:
        """Extract holdings from raw page text (fallback for non-table PDFs)."""
        results: list[BrokerHolding] = []
        lines = text.split("\n")

        for i, line in enumerate(lines):
            isin_match = ISIN_RE.search(line)
            if not isin_match:
                continue

            isin = isin_match.group(1)
            if isin in seen_isins:
                continue

            # Company name: text on same line or previous line
            company_name = self._extract_name_from_line(line, isin)
            if not company_name and i > 0:
                company_name = lines[i - 1].strip()

            # Quantity: look for numbers on same line or next line
            quantity = self._find_quantity_in_text(line)
            if quantity is None and i + 1 < len(lines):
                quantity = self._find_quantity_in_text(lines[i + 1])
            if quantity is None or quantity <= 0:
                continue

            symbol = resolve_isin(isin, company_name)
            if not symbol:
                logger.warning(
                    "Skipping unresolvable ISIN %s (%s)", isin, company_name
                )
                continue

            seen_isins.add(isin)
            results.append(
                BrokerHolding(
                    symbol=symbol,
                    quantity=quantity,
                    avg_buy_price=0.0,
                    current_price=0.0,
                )
            )

        return results

    @staticmethod
    def _extract_company_name(
        row: list[str | None], row_text: str, isin: str
    ) -> str:
        """Try to extract company name from table row cells."""
        # Often the first non-empty cell that isn't the ISIN contains the name
        for cell in row:
            if not cell:
                continue
            cell_stripped = cell.strip()
            if cell_stripped and isin not in cell_stripped:
                # Skip pure numeric cells
                if not re.match(r"^[\d,.\-\s]+$", cell_stripped):
                    return cell_stripped

        # Fallback: text before the ISIN in the concatenated row
        idx = row_text.find(isin)
        if idx > 0:
            return row_text[:idx].strip()
        return ""

    @staticmethod
    def _extract_quantity(row: list[str | None]) -> float | None:
        """Extract the quantity (typically last numeric value in the row)."""
        # CAS tables usually have quantity as one of the last columns
        numbers: list[float] = []
        for cell in reversed(row or []):
            if not cell:
                continue
            cleaned = cell.strip().replace(",", "")
            try:
                val = float(cleaned)
                if val > 0 and val == int(val):  # Holdings are whole numbers
                    numbers.append(val)
            except ValueError:
                continue

        # Return the first integer-like number found from the right
        return numbers[0] if numbers else None

    @staticmethod
    def _extract_name_from_line(line: str, isin: str) -> str:
        """Extract company name from a text line containing an ISIN."""
        idx = line.find(isin)
        if idx > 0:
            name = line[:idx].strip().rstrip("-").strip()
            if name and not re.match(r"^[\d,.\-\s]+$", name):
                return name
        return ""

    @staticmethod
    def _find_quantity_in_text(line: str) -> float | None:
        """Find a whole-number quantity in a text line."""
        # Look for standalone numbers (not part of ISIN)
        numbers = re.findall(r"\b(\d{1,7}(?:\.\d{1,4})?)\b", line)
        for num_str in reversed(numbers):
            if num_str.startswith("INE"):
                continue
            try:
                val = float(num_str)
                if val > 0:
                    return val
            except ValueError:
                continue
        return None

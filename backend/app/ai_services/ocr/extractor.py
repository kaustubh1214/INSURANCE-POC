"""
OCR Extractor — Phase 2 stub.
Extracts structured data from uploaded documents using Tesseract.

Supported document types:
- Aadhaar card
- PAN card
- Medical bills
- Discharge summaries
- Lab reports
- Prescriptions
- Insurance forms
"""
import os
from pathlib import Path


class OCRExtractor:
    """
    Extracts text and structured fields from document images/PDFs.

    Phase 2 Implementation:
    - pytesseract for OCR
    - Document type detection via filename/content
    - Field-specific extractors per document type
    - Structured JSON output for form auto-fill
    """

    async def extract(self, file_path: str, document_type: str) -> dict:
        """
        Extract text and structured fields from a document.

        Args:
            file_path: Path to the uploaded file
            document_type: Type hint ("aadhaar", "pan", "medical_bill", etc.)

        Returns:
            {
                "raw_text": str,
                "structured_data": dict,  # Extracted fields
                "confidence": float,       # 0-1
                "document_type_detected": str,
            }
        """
        # Phase 2: Real implementation with pytesseract
        # try:
        #     import pytesseract
        #     from PIL import Image
        #     img = Image.open(file_path)
        #     text = pytesseract.image_to_string(img)
        #     structured = self._extract_fields(text, document_type)
        #     return {"raw_text": text, "structured_data": structured, "confidence": 0.85}
        # except Exception as e:
        #     return {"raw_text": "", "structured_data": {}, "confidence": 0.0, "error": str(e)}

        return {
            "raw_text": "[OCR not yet configured — Phase 2]",
            "structured_data": {},
            "confidence": 0.0,
            "document_type_detected": document_type,
            "status": "pending_phase2",
        }

    def _extract_fields(self, text: str, document_type: str) -> dict:
        """Extract structured fields based on document type."""
        extractors = {
            "aadhaar": self._extract_aadhaar_fields,
            "pan": self._extract_pan_fields,
            "medical_bill": self._extract_bill_fields,
            "prescription": self._extract_prescription_fields,
        }
        extractor = extractors.get(document_type, lambda t: {})
        return extractor(text)

    def _extract_aadhaar_fields(self, text: str) -> dict:
        import re
        fields = {}
        aadhaar_match = re.search(r"\b\d{4}\s\d{4}\s\d{4}\b", text)
        if aadhaar_match:
            fields["aadhaar_number"] = aadhaar_match.group()
        return fields

    def _extract_pan_fields(self, text: str) -> dict:
        import re
        fields = {}
        pan_match = re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text)
        if pan_match:
            fields["pan_number"] = pan_match.group()
        return fields

    def _extract_bill_fields(self, text: str) -> dict:
        """Extract hospital name, amount, date from medical bill."""
        import re
        fields = {}
        amount_match = re.search(r"(?:Total|Amount|Rs\.?)\s*:?\s*(\d+(?:,\d+)*(?:\.\d{2})?)", text, re.I)
        if amount_match:
            fields["amount"] = amount_match.group(1).replace(",", "")
        return fields

    def _extract_prescription_fields(self, text: str) -> dict:
        """Extract doctor name, date, medicines from prescription."""
        return {}  # Phase 2 implementation

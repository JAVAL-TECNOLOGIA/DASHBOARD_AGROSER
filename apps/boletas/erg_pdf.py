"""Boletas mensuales de empleados en régimen general y agrario."""
from .modern_pdf import build_pdf as build_modern_pdf


def build_pdf(data, signature_path=None, employer_signature_path=None, delivery=None):
    return build_modern_pdf(
        data,
        signature_path=signature_path,
        employer_signature_path=employer_signature_path,
        delivery=delivery,
        weekly=False,
    )

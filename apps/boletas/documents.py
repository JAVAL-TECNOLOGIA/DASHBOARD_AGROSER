"""Identificadores numéricos usados por trabajadores nacionales y extranjeros."""


def valid_worker_document(value):
    return isinstance(value, str) and value.isascii() and value.isdecimal() and len(value) in (8, 9)

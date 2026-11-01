"""Busca estritamente local e de leitura no índice existente do segundo cérebro."""
from pathlib import Path
from contextlib import closing
import re
import sqlite3


class MemoryUnavailable(Exception):
    pass


def search(root: str | None, query: str, limit: int):
    if not root:
        raise MemoryUnavailable("Segundo cérebro ainda não configurado")
    base = Path(root).resolve()
    index = (base / "90-Config" / "memoria.sqlite").resolve()
    if not index.is_relative_to(base) or not index.is_file():
        raise MemoryUnavailable("Índice local indisponível; use a reindexação do segundo cérebro")
    words = re.findall(r"\w+", query, re.UNICODE)
    if not words:
        return []
    expression = " AND ".join('"' + word + '"' for word in words)
    try:
        with closing(sqlite3.connect(index.as_uri() + "?mode=ro", uri=True, timeout=2)) as connection:
            # Limita o trabalho da consulta, além do número de resultados.
            connection.set_progress_handler(lambda: 1, 1_000_000)
            rows = connection.execute(
                'SELECT title,source,path,ref,snippet(memory,1,"[","]"," … ",35) '
                'FROM memory WHERE memory MATCH ? ORDER BY bm25(memory) LIMIT ?',
                (expression, limit),
            ).fetchall()
    except sqlite3.Error:
        raise MemoryUnavailable("Busca local indisponível; verifique o índice") from None
    results = []
    for title, source, path, reference, excerpt in rows:
        resolved = (base / path).resolve()
        if not resolved.is_relative_to(base):
            continue
        results.append({"title": title[:300], "source": source, "path": path,
                        "reference": reference, "excerpt": excerpt[:2000], "classification": "private"})
    return results

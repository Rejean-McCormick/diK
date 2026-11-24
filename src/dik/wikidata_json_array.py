"""Read a JSON *array* of objects incrementally, even if its filename says .jsonl.

The cursor always points just after the last complete object. No third-party
packages are needed. The JSON parser validates each object; the envelope
scanner validates the comma-separated array structure. Values are bounded.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import BinaryIO, Iterator


class ArraySyntaxError(ValueError):
    """Malformed top-level JSON array; never treat as absence of identifiers."""


@dataclass(frozen=True)
class ArrayRecord:
    obj: object
    start: int
    end: int
    line: int
    next_line: int


def _nonspace(stream: BinaryIO, line: int) -> tuple[bytes, int]:
    while True:
        c = stream.read(1)
        if c not in (b' ', b'\t', b'\r', b'\n'):
            return c, line
        if c == b'\n':
            line += 1


def _value(stream: BinaryIO, start: int, line: int, limit: int) -> ArrayRecord:
    # '{' has already been consumed; collect one balanced object and rewind
    # the unused part of a line (including the next comma/array end).
    data = bytearray(b'{')
    level = 1
    quoted = False
    escaped = False
    while True:
        remaining = limit - len(data)
        if remaining <= 0:
            raise ArraySyntaxError('Objet JSON depasse la limite par element')
        begin = stream.tell()
        chunk = stream.readline(min(65536, remaining + 1))
        if not chunk:
            raise ArraySyntaxError('Fin du tableau pendant un objet')
        for i, b in enumerate(chunk):
            if quoted:
                if escaped:
                    escaped = False
                elif b == 92:
                    escaped = True
                elif b == 34:
                    quoted = False
            elif b == 34:
                quoted = True
            elif b in (123, 91):  # { [
                level += 1
            elif b in (125, 93):  # } ]
                level -= 1
                if level == 0:
                    segment = chunk[:i+1]
                    data.extend(segment)
                    if len(data) > limit:
                        raise ArraySyntaxError('Objet JSON depasse la limite par element')
                    stream.seek(begin + i + 1)
                    try:
                        parsed = json.loads(data.decode('utf-8'))
                    except (UnicodeError, ValueError) as exc:
                        raise ArraySyntaxError('Objet JSON non valide') from exc
                    return ArrayRecord(parsed, start, stream.tell(), line,
                                       line + data.count(b'\n'))
                if level < 0:
                    raise ArraySyntaxError('Delimiteurs non equilibres')
        data.extend(chunk)
        if len(data) > limit:
            raise ArraySyntaxError('Objet JSON depasse la limite par element')


def iter_objects(stream: BinaryIO, *, offset: int = 0, line: int = 1,
                 max_item_bytes: int = 2_000_000) -> Iterator[ArrayRecord]:
    """Yield one element at a time, restoring a trusted (offset,line) cursor.

    On resume, ``offset`` points right after a yielded element, before the
    separating comma or the closing ']'. A source SHA/versioned checkpoint
    authorises this cursor; arbitrary user offsets should not be accepted.
    """
    stream.seek(offset)
    if offset == 0:
        first, line = _nonspace(stream, line)
        if first == b'\xef':
            if stream.read(2) != b'\xbb\xbf':
                raise ArraySyntaxError('BOM JSON invalide')
            first, line = _nonspace(stream, line)
        if first != b'[':
            raise ArraySyntaxError('Tableau JSON attendu')
        at_first = True
    else:
        at_first = False
    while True:
        char, line = _nonspace(stream, line)
        if at_first:
            if char == b']':
                break
            if char != b'{':
                raise ArraySyntaxError('Objet JSON attendu dans tableau')
        else:
            if char == b']':
                break
            if char != b',':
                raise ArraySyntaxError('Separateur du tableau absent')
            char, line = _nonspace(stream, line)
            if char != b'{':
                raise ArraySyntaxError('Objet JSON absent apres virgule')
        start = stream.tell() - 1
        record = _value(stream, start, line, max_item_bytes)
        yield record
        line = record.next_line
        at_first = False
    tail, _ = _nonspace(stream, line)
    if tail:
        raise ArraySyntaxError('Contenu apres le tableau JSON')


def peek_array(path) -> bool:
    """Detect '[' (with optional UTF-8 BOM and whitespace), not by extension."""
    with open(path, 'rb') as stream:
        head = stream.read(1024)
    return head.lstrip(b'\xef\xbb\xbf \t\r\n').startswith(b'[')

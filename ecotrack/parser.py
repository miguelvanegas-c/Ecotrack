"""Detección de actividades en lenguaje natural (español / inglés sencillo)."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from ecotrack.catalog import ALL_ITEMS, CatalogItem

_WORD_NUMBERS = {
    "un": 1.0,
    "una": 1.0,
    "uno": 1.0,
    "dos": 2.0,
    "tres": 3.0,
    "cuatro": 4.0,
    "cinco": 5.0,
    "seis": 6.0,
    "siete": 7.0,
    "ocho": 8.0,
    "nueve": 9.0,
    "diez": 10.0,
    "once": 11.0,
    "doce": 12.0,
    "quince": 15.0,
    "veinte": 20.0,
    "media": 0.5,
    "medio": 0.5,
}

_NUM = r"(?:\d+(?:[.,]\d+)?|" + "|".join(sorted(_WORD_NUMBERS, key=len, reverse=True)) + r")"
_QTY_RE = re.compile(
    rf"(?<![a-z0-9])({_NUM})\s*"
    rf"(km|kilometros|kilometro|horas|hora|hrs|hr|h|minutos|minuto|mins|min)?(?![a-z])",
    re.IGNORECASE,
)


@dataclass
class DetectedActivity:
    item: CatalogItem
    quantity: float
    kg_co2: float
    matched: str
    assumed_default: bool = False


@dataclass
class ParseResult:
    original: str
    activities: list[DetectedActivity] = field(default_factory=list)

    @property
    def total_kg(self) -> float:
        return round(sum(a.kg_co2 for a in self.activities), 2)

    def by_category(self) -> dict[str, float]:
        totals = {"food": 0.0, "transport": 0.0, "energy": 0.0}
        for act in self.activities:
            totals[act.item.category] += act.kg_co2
        return {k: round(v, 2) for k, v in totals.items()}


def normalize(text: str) -> str:
    text = text.lower().replace("ñ", "n")
    nfkd = unicodedata.normalize("NFD", text)
    stripped = "".join(ch for ch in nfkd if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", stripped).strip()


def _parse_number(raw: str) -> float:
    key = raw.lower().replace(",", ".")
    if key in _WORD_NUMBERS:
        return _WORD_NUMBERS[key]
    return float(key)


def _is_boundary(text: str, start: int, end: int) -> bool:
    left_ok = start == 0 or not text[start - 1].isalnum()
    right_ok = end >= len(text) or not text[end].isalnum()
    return left_ok and right_ok


def _negated(text: str, start: int) -> bool:
    prefix = text[max(0, start - 24) : start]
    return bool(re.search(r"\bno\s+(?:\w+\s+){0,2}$", prefix))


def _looks_ahead_unit(text: str, match_end: int) -> str:
    tail = text[match_end : match_end + 16]
    m = re.match(r"\s*(km|kilometros|kilometro|horas|hora|hrs|hr|h|minutos|minuto|mins|min)\b", tail)
    return (m.group(1) if m else "").lower()


def _quantity_for(item: CatalogItem, text: str, start: int, end: int) -> tuple[float, bool]:
    left = max(0, start - 70)
    right = min(len(text), end + 70)
    window = text[left:right]
    kw_from = start - left
    kw_to = end - left
    matches = list(_QTY_RE.finditer(window))
    if not matches:
        return item.default_qty, True

    def dist_to_kw(m: re.Match[str]) -> int:
        return min(abs(m.end() - kw_from), abs(m.start() - kw_to))

    def score(m: re.Match[str]) -> float:
        unit = (m.group(2) or "").lower() or _looks_ahead_unit(window, m.end())
        dist = dist_to_kw(m)
        before = m.end() <= kw_from + 1
        if item.category == "food":
            if unit or not before or dist > 12:
                return -100
            return 50 - dist
        if item.category == "transport":
            if not (unit.startswith("km") or unit.startswith("kilo")):
                return -50
            if dist > 36:
                return -40
            return 80 - dist
        if item.is_cycle:
            if unit or not before or dist > 12:
                return -20
            return 50 - dist
        if unit not in {"h", "hr", "hrs", "hora", "horas", "min", "mins", "minuto", "minutos"}:
            return -30
        if dist > 18:
            return -25
        return 80 - dist

    best = max(matches, key=score)
    if score(best) < 0:
        return item.default_qty, True

    value = _parse_number(best.group(1))
    unit = (best.group(2) or "").lower() or _looks_ahead_unit(window, best.end())
    if item.category == "energy" and not item.is_cycle:
        if unit in {"min", "mins", "minuto", "minutos"}:
            value = value / 60.0
    return value, False


def _keyword_index() -> list[tuple[str, CatalogItem]]:
    pairs: list[tuple[str, CatalogItem]] = []
    for item in ALL_ITEMS:
        for kw in item.keywords:
            pairs.append((normalize(kw).strip(), item))
    pairs.sort(key=lambda p: len(p[0]), reverse=True)
    return pairs


_KEYWORDS = _keyword_index()


def parse_diary(text: str) -> ParseResult:
    original = text.strip()
    if not original:
        return ParseResult(original=original)

    norm = " " + normalize(original) + " "
    used = [False] * len(norm)
    found: list[DetectedActivity] = []

    for keyword, item in _KEYWORDS:
        if not keyword:
            continue
        search_from = 0
        while True:
            idx = norm.find(keyword, search_from)
            if idx == -1:
                break
            end = idx + len(keyword)
            search_from = idx + 1
            if any(used[idx:end]):
                continue
            if not _is_boundary(norm, idx, end):
                continue
            if _negated(norm, idx):
                continue

            qty, assumed = _quantity_for(item, norm, idx, end)
            kg = round(qty * item.factor, 3)
            for i in range(idx, end):
                used[i] = True
            found.append(
                DetectedActivity(
                    item=item,
                    quantity=qty,
                    kg_co2=kg,
                    matched=keyword.strip(),
                    assumed_default=assumed,
                )
            )

    found.sort(key=lambda a: a.kg_co2, reverse=True)
    return ParseResult(original=original, activities=found)

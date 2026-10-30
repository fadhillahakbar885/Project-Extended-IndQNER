import re, unicodedata

ENCLITICS = ['-lah', '-pun', '-kah', '-nya', '-ku', '-mu', 'lah', 'pun', 'kah', 'nya', 'ku', 'mu']

COMMON_WORDS_BLACKLIST = {
    "ada", "adalah", "hari", "dan", "jika", "bila", "dari", "pada", "oleh", "bagi", 
    "itu", "ini", "dia", "ia", "kami", "kamu", "mereka", "kita", "bisa", "akan", 
    "telah", "belum", "sudah", "hanya", "juga", "lagi", "pun", "lah", "apa", "siapa",
    "mana", "kapan", "mengapa", "bagaimana", "satu", "dua", "tiga", "empat", "lima",
    "enam", "tujuh", "delapan", "sembilan", "sepuluh", "orang", "atas", "bawah"
}

def normalize_text(text: str) -> str:
    """
    Normalizes transliteration quotes (ayn, hamzah) to standard apostrophe without stripping.
    Preserves exact string length and boundary spaces for 1:1 offset integrity.
    """
    if not text:
        return ""
    return text.replace('‘', "'").replace('’', "'").replace('`', "'").replace('ʻ', "'")

def clean_footnotes(text: str) -> str:
    """
    Cleans footnotes markers like 1), 2), 31) from Kemenag text without disturbing
    normal explanatory parentheses like (Al-Qur'an) or (Sinai).
    Footnotes are strictly digits followed by closing parenthesis: \\d+\\)
    """
    if not text:
        return ""
    # Pattern: optional space followed by digits and closing paren
    cleaned = re.sub(r'\s*\b\d+\)', '', text)
    # Also handle trailing digits with paren like 'jahil.”31)' -> 'jahil.”'
    cleaned = re.sub(r'\d+\)', '', cleaned)
    return cleaned

def clean_token_for_matching(token_str: str) -> str:
    """Strips punctuation and enclitics (-lah, -pun, etc.) temporarily for similarity calculation."""
    t = token_str.strip(".,;:!?\"'()«»“”[]")
    norm_t = normalize_text(t)
    lower_t = norm_t.lower()
    for enc in ENCLITICS:
        if lower_t.endswith(enc) and len(lower_t) > len(enc) + 2:
            return norm_t[:-len(enc)].strip("-")
    return norm_t

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculates Levenshtein edit distance between two strings."""
    s1_norm = normalize_text(s1).lower()
    s2_norm = normalize_text(s2).lower()
    if len(s1_norm) < len(s2_norm):
        return levenshtein_distance(s2_norm, s1_norm)
    if len(s2_norm) == 0:
        return len(s1_norm)
    previous_row = range(len(s2_norm) + 1)
    for i, c1 in enumerate(s1_norm):
        current_row = [i + 1]
        for j, c2 in enumerate(s2_norm):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def string_similarity(s1: str, s2: str) -> float:
    """Calculates normalized string similarity ratio between 0.0 and 1.0."""
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    dist = levenshtein_distance(s1, s2)
    return 1.0 - (dist / max_len)

def tokenize_with_offsets(text: str):
    """
    Tokenizes Indonesian text into word tokens with exact character spans (start_char, end_char).
    Separates punctuation tokens cleanly.
    """
    # Regex splits words, numbers, and separate punctuation marks
    pattern = re.compile(r"[\w‘'’-]+|[^\w\s]")
    tokens = []
    for match in pattern.finditer(text):
        tok_str = match.group()
        start = match.start()
        end = match.end()
        tokens.append({
            "text": tok_str,
            "start": start,
            "end": end
        })
    return tokens

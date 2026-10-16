import re

AI_KEYWORDS = [
    r'\bAI\b', r'\bartificial intelligence\b', r'\bmachine learning\b',
    r'\bLLM\b', r'\bagent\b', r'\bgenerative AI\b', r'\bdeep learning\b',
    r'\bneural network\b', r'\bNLP\b', r'\bcomputer vision\b'
]

LOCATION_KEYWORDS = [
    r'\bremote\b', r'\bonline\b', r'\bvirtual\b',
    r'\bVigo\b', r'\bSpain\b', r'\bEspaña\b', r'\bGalicia\b'
]

AI_ALLOWED_PHRASES = [
    r'AI tools allowed', r'vibe coding', r'use any tools',
    r'Copilot.{0,20}allowed', r'Cursor.{0,20}allowed',
    r'AI.assisted development welcome'
]

AI_PROHIBITED_PHRASES = [
    r'no AI generated code', r'must write own code',
    r'AI assistance prohibited', r'no AI tools', r'original code only'
]

def is_ai_topic(hackathon: dict) -> bool:
    text = f"{hackathon.get('title', '')} {hackathon.get('description', '')}".lower()
    return any(re.search(kw, text, re.IGNORECASE) for kw in AI_KEYWORDS)

def is_location_match(hackathon: dict) -> bool:
    text = f"{hackathon.get('location', '')} {hackathon.get('description', '')}".lower()
    return any(re.search(kw, text, re.IGNORECASE) for kw in LOCATION_KEYWORDS)

def allows_ai_coding(hackathon: dict) -> bool:
    text = hackathon.get('description', '').lower()
    has_prohibited = any(re.search(p, text, re.IGNORECASE) for p in AI_PROHIBITED_PHRASES)
    if has_prohibited:
        return False
    has_allowed = any(re.search(p, text, re.IGNORECASE) for p in AI_ALLOWED_PHRASES)
    if has_allowed:
        return True
    return True

def apply_all(hackathon: dict) -> bool:
    return is_ai_topic(hackathon) and is_location_match(hackathon) and allows_ai_coding(hackathon)
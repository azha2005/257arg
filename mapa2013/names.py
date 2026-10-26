import re, unicodedata
def norm(s):
    s = s.replace('', '')
    s = unicodedata.normalize('NFKD', s); s = ''.join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r'\.', '. ', s)
    s = re.sub(r'\b(gnral|gral)\b\.?', 'general', s); s = re.sub(r'\b(crnel|cnel)\b\.?', 'coronel', s)
    s = re.sub(r'\bsn\b', 'san', s); s = re.sub(r'\b(gobernador|governador|gdor)\b\.?', 'gobernador', s)
    s = re.sub(r'[^a-z0-9]', '', s)       # clave sin espacios
    return s

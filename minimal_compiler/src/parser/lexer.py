import re
from collections import namedtuple

Token = namedtuple("Token", ["type", "text", "pos"])

# (TOKEN_NAME, REGEX)
token_specification = [
    ('WHILE',   r'(?i:while)\b'),
    ('DO',      r'(?i:do)\b'),
    ('END',     r'(?i:end)\b'),
    ('ASSIGN',  r'='),
    ('PRINT',   r'(?i:echo)\b'), # for debugging the self-compiler (not part of the original WHILE language)
    ('PLUS',    r'\+'),
    ('MINUS',   r'-'),
    ('GREATER', r'>'),
    ('SEMI',    r';'),
    ('VAR',     r'x(?:[1-9][0-9]*|0)\b'),
    ('CONST',   r'(?:[1-9][0-9]*|0)\b'),
    ('WS',      r'[ \t\r\n]+'),
    ('COMMENT', r'/[^\n]*'),
    ('BLOCK_COMMENT', r'/\*(.|\n)*?\*/'),
]

token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
master_pattern = re.compile(token_regex)

def tokenize(input_text):
    pos = 0
    tokens = []
    while pos < len(input_text):
        m = master_pattern.match(input_text, pos)
        if m:
            typ = m.lastgroup
            text = m.group(typ)

            # ignore whitespace and comments
            if typ not in ('WS', 'COMMENT', 'BLOCK_COMMENT'):
                tokens.append(Token(typ, text, pos))
            pos = m.end()
        else:
            raise RuntimeError(f'LexerException: Unexpected symbol {input_text[pos]!r} at {pos}')
        
    tokens.append(Token("EOF", "", pos)) # always used as last token
    return tokens
import keyword

def isIdentifier(word):
    return word.isidentifier() and not keyword.iskeyword(word)

def column_string(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

def column_string_to_int(col):
    val = 0
    for i, c in enumerate(reversed(col)):
        val += (ord(c) - 64) * (26 ** i)
    return val - 1
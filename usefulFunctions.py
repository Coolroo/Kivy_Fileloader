import keyword

def isIdentifier(word):
    return word.isidentifier() and not keyword.iskeyword(word)
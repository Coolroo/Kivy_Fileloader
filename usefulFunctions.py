import keyword

def isIdentifier(word):
    """
    The isIdentifier function returns True if the word is a valid identifier, and False otherwise. 
    A valid identifier is a string that begins with an alphabetic character or underscore (_), and only consists of alphanumeric characters (i.e., it does not allow punctuation, white space, or special characters).
    
    :param word: Used to Check if the word is a valid identifier.
    :return: A boolean value.
    
    :doc-author: Trelent
    """
    return word.isidentifier() and not keyword.iskeyword(word)

def column_string(n):
    """
    The column_string function converts a column number into a string that Excel will recognize as a column name.
       For example, 1 -> A, 26 -> Z, 27 -> AA, 703 -> AAA.
    
    :param n: The row index to be converted
    :return: The alphabetical column string for an integer.
    
    :doc-author: Trelent
    """
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

def column_string_to_int(col):
    """
    The column_string_to_int function converts a column string into an integer.
       For example, the input 'A' will return 0, while the input 'B' will return 1.
       The function is intended to be used in conjunction with pandas dataframes and series.
    
    :param col: Used to Pass the column string to be converted.
    :return: The integer representation of a column string.
    
    :doc-author: Trelent
    """
    val = 0
    for i, c in enumerate(reversed(col)):
        val += (ord(c) - 64) * (26 ** i)
    return val - 1
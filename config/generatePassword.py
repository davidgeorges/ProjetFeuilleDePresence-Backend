import random

#Generate the first password for the new user
def generate_password():
    char_seq1 = "abcdefghijklmnopqrstuvwxyz"
    char_seq2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    char_seq3 = "0123456789"
    char_seq4 = "!$%&*+,-./:;<=?@[^_{|~"
    password = ''
    for i in range(7):
        random_char = random.choice(char_seq1) + random.choice(char_seq2) + random.choice(char_seq3) + random.choice(char_seq4)
        password += random_char
    return password

from string import ascii_lowercase, ascii_uppercase, ascii_letters

def get_list(input, key):
    index_list = []
    every = ('All', [])
    non_letter = ('0-9', [])
    lowercase = ('a-z', [])
    uppers = []
    for u in ascii_uppercase:
        upper = (u, [])
        uppers.append(upper)
    #for c in printable:
    for i in input:
        name = i.get(key,'empty')
        if name == '':
            name = ' '
        every[1].append(name)
        letter = list(name)[0]
        if letter not in (ascii_letters):
            non_letter[1].append(name)
        elif letter in (ascii_lowercase):
            lowercase[1].append(name)
        elif letter in ascii_uppercase:
            for u in uppers:
                if letter == u[0]:
                    u[1].append(name)

    index_list.append(every)
    if len(non_letter[1]) > 0:
        index_list.append(non_letter)
    if len(lowercase[1]) > 0:
        index_list.append(lowercase)
    for u in uppers:
        if len(u[1]) > 0:
            index_list.append(u)
    return index_list
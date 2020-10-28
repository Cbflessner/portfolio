def ngrams(input, n):
    input = input.split(' ')
    output = []
    for i in range(len(input)-n+1):
        output.append(input[i:i+n])
    return output

def remove_special(input):
    clean = ''.join(ch for ch in input if ch.isalnum())
    return clean
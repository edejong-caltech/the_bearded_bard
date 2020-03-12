import sonnet_helper as sh 
import string
sonnets = sh.load_sonnet_text('shakespeare.txt')

punct = []

for sonnet in sonnets:
    for line in sonnet:
        for word in line:
            for c in word:
                if c in string.punctuation:
                    punct.append(c)

punct = set(punct)
print(punct)
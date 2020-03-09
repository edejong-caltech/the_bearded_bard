'''
sonnet_helper.py
authors: Emily de Jong, Daniel Mukasa

Description : Helper functions for sonnet data processing
'''
def load_sonnet_text(filename):
    sonnets = []
    sonnet_i = []
    # import the raw data
    data = open(filename,'r')
    #lines = data.readlines()
    #Nlines = len(lines)

    # if the line starts with a number 
    while True:
        line = data.readline()
        if not line:
            break
        #print(line)
        text = line.lower().split()
        if len(text) > 0: # ignore empty lines
            #print(text)
            # if the line starts with a number, begin a new sonnet
            if text[-1].isdigit():
                sonnet_line = 0
                if len(sonnet_i) > 0:
                    sonnets.append(sonnet_i)
                sonnet_i = []
            # otherwise, append each word
            else:
                sonnet_i.append([])
                for word in text:
                    # remove line-end and intermediate punctuation
                    word = word.strip(".,?:;")
                    sonnet_i[sonnet_line].append(word)
                #sonnet_i[sonnet_line].append('\n')
                sonnet_line += 1
    sonnets.append(sonnet_i)
    data.close()
    return sonnets

# get a list of rhyming word pairs; make sure each pair is unique
def get_rhymes(sonnets):
    rhymes = []
    for sonnet in sonnets:
        # discard if there are more or fewer than 14 lines
        if len(sonnet) == 14: 
            rhymes.append([sonnet[0][-1], sonnet[2][-1]])
            rhymes.append([sonnet[1][-1], sonnet[3][-1]])
            rhymes.append([sonnet[4][-1], sonnet[6][-1]])
            rhymes.append([sonnet[5][-1], sonnet[7][-1]])
            rhymes.append([sonnet[8][-1], sonnet[10][-1]])
            rhymes.append([sonnet[9][-1], sonnet[11][-1]])
            rhymes.append([sonnet[12][-1], sonnet[13][-1]])
        # Note: may contain duplicates
    return rhymes

def get_dictionary(sonnets):
    word_list = []
    for sonnet in sonnets:
        for line in sonnet:
            for word in line:
                word_list.append(word)
    # now get rid of duplicates
    word_set = set(word_list)
    word_list = list(word_set)
    dictionary = {word : i for i,word in enumerate(word_list)}

    return dictionary

def sonnets_to_seqs(sonnets):
    # could go by line, stanza, or poem... let's go by poem for now
    N_sonnets = len(sonnets)
    seqs = [[] for _ in range(N_sonnets)]
    for i, sonnet in enumerate(sonnets):
        for line in sonnet:
            for word in line:
                seqs[i].append(word)
    return seqs


'''
POSTPROCESING:
'''
# def convert_emission_to_sonnet(emission, dictionary)
### takes an emission in the form of a sequence of ints and converts it back to a sonnet using the dictionary
# return sonnet

# def fix_grammar(sonnet):
### check for proper capitalization rules, punctuation, etc.
# pass

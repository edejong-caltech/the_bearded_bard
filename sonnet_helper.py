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
                    word = word.strip(".,?:;()!")
                    word = word.strip(".'")
                    word = word.strip(',')
                    word = word.strip('!')
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

def generate_naive_sonnet(hmm, M):
    from HMM import HiddenMarkovModel
    '''
    Generates a naive sonnet of 14 lines, each line with length M, assuming that the starting state
    is chosen uniformly at random. 

    Arguments:
        M:          Number of words per line in the sonnet

    Returns:
        sonnet:     The randomly generated sonnet as a list.
        states:     The randomly generated states as a list.
    '''
  
    M_tot = 14 * M
    sonnet_word_ids, states = hmm.generate_emission(M_tot)
    words = list(hmm.dictionary.keys())
    sonnet_words = []

    # convert the integer list back to a sequence of words
    for ids in sonnet_word_ids:
        sonnet_words.append(words[ids])

    # now convert this to a 14 line sonnet
    sonnet = []
    for i in range(14):
        line = sonnet_words[M*i:M*i + M]
        line = fix_grammar(line)
        line = ' '.join(line)
        sonnet.append(line)

    return sonnet

def generate_sonnet_syllables(hmm):
    from HMM import HiddenMarkovModel
    '''
    Generates a sonnet of 14 lines with 10 syllables per line, assuming that the starting state
    is chosen uniformly at random. 

    Arguments:
        M:          Number of words per line in the sonnet

    Returns:
        sonnet:     The randomly generated sonnet as a list.
        states:     The randomly generated states as a list.
    '''
    words = list(hmm.dictionary.keys())
    data = open('Syllable_dictionary.txt','rb')
    syllable_dict = []
    syllable_end_dict = []

    # First create a dictionary corresponding to the syllable/word pairs
    while True:
        entry = data.readline().decode()
        if not entry:
            break
        entry = entry.split()
        if len(entry) == 3:
            [word, syl1, syl2] = entry
            if 'E' in syl1:
                end_syl = int(syl1.strip('E'))
                num_syl = syl2
            elif 'E' in syl2:
                end_syl = int(syl2.strip('E'))
                num_syl = syl1
            syllable_end_dict.append([word,end_syl])
            
        else:
            [word, num_syl] = entry
            syllable_end_dict.append([word,int(num_syl)])

        num_syl = int(num_syl)
        syllable_dict.append([word,num_syl])
        
    syllable_dict = dict(syllable_dict)
    syllable_end_dict = dict(syllable_end_dict)

    data.close()

    # Now generate a sonnet:
    sonnet = []
    # first word of first line:
    next_word_id, next_state = hmm.generate_emission(1)
    next_word = words[next_word_id[0]]
    next_state = next_state*2 # for consistency with others

    for i in range(14):
        total_it = 0
        syllable_count = 0
        line_i = []
        while total_it < 100: # give up at some point
            try:
                next_word_syl = syllable_dict[next_word]
            except KeyError:
                next_word_id, next_state = hmm.generate_emission(1,start_state = prev_state)
                next_word = words[next_word_id[0]]
                continue

            syllable_count += next_word_syl
            # if adding the word doesn't take us over 14 syllables, add the word and keep going
            if syllable_count < 10:
                line_i.append(next_word)
                prev_state = next_state[-1]

            # if it takes us exactly to 10 syllables...
            elif syllable_count == 10:
                # first verify that the end syllable count isn't different
                next_word_syl_end = syllable_end_dict[next_word]
                # ***if it isn't different, then we have finished the line; break out of the while loop
                if next_word_syl_end == next_word_syl:
                    line_i.append(next_word)
                    prev_state = next_state[-1]
                    break

                # if it's higher, discard the word and try again
                elif next_word_syl_end > next_word_syl:
                    syllable_count -= next_word_syl

                # if it's lower, accept the word and continue
                elif next_word_syl_end < next_word_syl:
                    line_i.append(next_word)
                    prev_state = next_state[-1]
            
            # if we go over the number of syllables, discard the word and try again
            elif syllable_count > 10:
                syllable_count -= next_word_syl
            
            next_word_id, next_state = hmm.generate_emission(1,start_state = prev_state)
            next_word = words[next_word_id[0]]

            total_it += 1

        # once we have generated a 10 syllable line, add it and restart the counters
        sonnet.append(line_i)
    
    # now convert the lines to lines and fix the grammar
    sonnet_final = []
    for line in sonnet:
        line = fix_grammar(line)
        line = ' '.join(line)
        sonnet_final.append(line)

    return sonnet_final

def fix_grammar(line):
### check for proper capitalization rules, punctuation, etc.
    line[0] = line[0].capitalize()
    for i, word in enumerate(line):
        if word == ('i' or "i'm" or "i've" or "i'd"):
            line[i] = line[i].capitalize()
    return line



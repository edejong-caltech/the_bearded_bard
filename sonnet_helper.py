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
            rhymes.append([sonnet[2][-1], sonnet[0][-1]])
            rhymes.append([sonnet[1][-1], sonnet[3][-1]])
            rhymes.append([sonnet[3][-1], sonnet[1][-1]])
            rhymes.append([sonnet[4][-1], sonnet[6][-1]])
            rhymes.append([sonnet[6][-1], sonnet[4][-1]])
            rhymes.append([sonnet[5][-1], sonnet[7][-1]])
            rhymes.append([sonnet[7][-1], sonnet[5][-1]])
            rhymes.append([sonnet[8][-1], sonnet[10][-1]])
            rhymes.append([sonnet[10][-1], sonnet[8][-1]])
            rhymes.append([sonnet[9][-1], sonnet[11][-1]])
            rhymes.append([sonnet[11][-1], sonnet[9][-1]])
            rhymes.append([sonnet[12][-1], sonnet[13][-1]])
            rhymes.append([sonnet[13][-1], sonnet[12][-1]])
        # Note: may contain duplicates
    
    rhymes = dict(rhymes)
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

def sonnets_to_seqs(sonnets, by_line=False, N_lines = 2155):
    # could go by line, stanza, or poem... let's go by poem for now
    N_sonnets = len(sonnets)
    N_seqs = N_sonnets
    if by_line:
        N_seqs = N_lines
    seqs = [[] for _ in range(N_seqs)]
    i_line = 0
    for i, sonnet in enumerate(sonnets):
        for line in sonnet:
            for word in line:
                if by_line:
                    seqs[i_line].append(word)
                else:
                    seqs[i].append(word)
            i_line += 1
    return seqs


'''
POSTPROCESING:
'''
# def convert_emission_to_sonnet(emission, dictionary)
### takes an emission in the form of a sequence of ints and converts it back to a sonnet using the dictionary
# return sonnet

def generate_naive_sonnet(hmm, M=8):
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

def generate_sonnet_syllables(hmm, N_lines=14,start_state='',fix_grammar_on = True):
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
    syllable_dict, syllable_end_dict = get_syllable_dict(hmm)

    # Now generate a sonnet:
    sonnet = []
    states = []
    # first word of first line:
    if start_state == '':
        next_word_id, next_state = hmm.generate_emission(1)
        next_word = words[next_word_id[0]]
        next_state = next_state*2 # for consistency with others
        prev_state = next_state[0]
    else:
        next_word_id, next_state = hmm.generate_emission(1,start_state = start_state)
        next_word = words[next_word_id[0]]
        next_state = next_state*2 # for consistency with others
        prev_state = start_state

    for i in range(N_lines):
        total_it = 0
        syllable_count = 0
        line_i = []

        if i > 0:
            next_word_id, next_state = hmm.generate_emission(1,start_state = prev_state)
            next_word = words[next_word_id[0]]

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
                states.append(next_state[-1])
                prev_state = next_state[-1]

            # if it takes us exactly to 10 syllables...
            elif syllable_count == 10:
                # first verify that the end syllable count isn't different
                next_word_syl_end = syllable_end_dict[next_word]
                # ***if it isn't different, then we have finished the line; break out of the while loop
                if next_word_syl_end == next_word_syl:
                    line_i.append(next_word)
                    states.append(next_state[-1])
                    prev_state = next_state[-1]
                    break

                # if it's higher, discard the word and try again
                elif next_word_syl_end > next_word_syl:
                    syllable_count -= next_word_syl

                # if it's lower, accept the word and continue
                elif next_word_syl_end < next_word_syl:
                    line_i.append(next_word)
                    states.append(next_state[-1])
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
        if fix_grammar_on:
            line = fix_grammar(line)
        line = ' '.join(line)
        sonnet_final.append(line)

    return sonnet_final, states

def generate_rhyming_sonnet(hmm, rhymes):
    sonnet = []
    states = []
    syl_dict, end_syl_dict = get_syllable_dict(hmm)
   
    for stanza in range(3):
        # generate the rhyme-determining lines, which are 1,2
        # line 1:
        while True:
            if stanza == 0:
                start_state = ''
            else:
                start_state = states_4[-1]

            line_1, states_1 = generate_sonnet_syllables(hmm, N_lines=1,start_state = start_state,fix_grammar_on = False)
            #print(line_1[0].split()[-1])
            if line_1[0].split()[-1] in rhymes:
                sonnet.append(line_1)
                states.append(states_1)
                #print(line_1)
                break
            else:
                continue

        # line 2:
        while True:
            line_2, states_2 = generate_sonnet_syllables(hmm, N_lines=1, start_state=states_1[-1],fix_grammar_on = False) # end of line 1 as start state
            #print(line_1[0].split()[-1])
            if line_2[0].split()[-1] in rhymes:
                sonnet.append(line_2)
                states.append(states_2)
                #print(line_2)
                break
            else:
                continue

        # line 3:
        while True:
            line_3, states_3 = generate_sonnet_syllables(hmm, N_lines=1, start_state=states_2[-1],fix_grammar_on = False) # end of line 2 as start state
            line_3 = line_3[0].split()
            #print(line_1[0].split()[-1])
            end_word_3 = rhymes[line_1[0].split()[-1]]
            if end_syl_dict[end_word_3] == end_syl_dict[line_3[-1]]:
                line_3[-1] = end_word_3
                line_3 = fix_grammar(line_3)
                line_3 =' '.join(line_3)
                sonnet.append(line_3)
                states.append(states_3)
                #print(line_3)
                break
            else:
                continue

        # line 4:
        while True:
            line_4, states_4 = generate_sonnet_syllables(hmm, N_lines=1, start_state=states_3[-1],fix_grammar_on = False) # end of line 2 as start state
            line_4 = line_4[0].split()
            #print(line_1[0].split()[-1])
            end_word_4 = rhymes[line_2[0].split()[-1]]
            if end_syl_dict[end_word_4] == end_syl_dict[line_4[-1]]:
                line_4[-1] = end_word_4
                line_4 = fix_grammar(line_4)
                line_4 =' '.join(line_4)
                sonnet.append(line_4)
                states.append(states_4)
                #print(line_4)
                break
            else:
                continue
    
    # quatrain: lines 13 and 14
    # line 13:
    while True:
        line_13, states_13 = generate_sonnet_syllables(hmm, N_lines=1, start_state=states_4[-1],fix_grammar_on = False) # end of line 1 as start state
        #print(line_1[0].split()[-1])
        if line_13[0].split()[-1] in rhymes:
            sonnet.append(line_13)
            states.append(states_13)
            #print(line_13)
            break
        else:
            continue

    # line 14:
    while True:
        line_14, states_14 = generate_sonnet_syllables(hmm, N_lines=1, start_state=states_13[-1],fix_grammar_on = False) # end of line 2 as start state
        line_14 = line_14[0].split()
        #print(line_1[0].split()[-1])
        end_word_14 = rhymes[line_13[0].split()[-1]]
        if end_syl_dict[end_word_14] == end_syl_dict[line_14[-1]]:
            line_14[-1] = end_word_14
            line_14 = fix_grammar(line_14)
            line_14 =' '.join(line_14)
            sonnet.append(line_14)
            states.append(states_14)
            #print(line_4)
            break
        else:
            continue

    # go through and fix the grammar on the rhyme-determining lines
    for i in [0,1,4,5,8,9,12]:
        line_i = sonnet[i][0].split()
        line_i = fix_grammar(line_i)
        sonnet[i] = ' '.join(line_i)
    
    #print(sonnet)

    return sonnet, states

def fix_grammar(line):
### check for proper capitalization rules, punctuation, etc.
    line[0] = line[0].capitalize()
    for i, word in enumerate(line):
        if word == ('i' or "i'm" or "i've" or "i'd"):
            line[i] = line[i].capitalize()
    return line

def get_syllable_dict(hmm):
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

    return syllable_dict, syllable_end_dict



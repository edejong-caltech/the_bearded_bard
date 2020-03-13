import sonnet_helper as sh
import pickle as pkl
from HMM import unsupervised_HMM

sonnets = sh.load_sonnet_text('shakespeare.txt')
dictionary = sh.get_dictionary(sonnets)
rhymes = sh.get_rhymes(sonnets)
seqs = sh.sonnets_to_seqs(sonnets,by_line = True)

N_states = 5 # can be changed
N_iters = 2 # can be changed

#hmm = unsupervised_HMM(seqs, N_states, dictionary, N_iters)
#file = open('5_state_2_iters.pkl','wb')
#pkl.dump(hmm,'5_state_2_iters.pkl')
#file.close()

file = open('HMMs/8_state_50_iters.pkl','rb')
hmm = pkl.load(file)
file.close()

#new_sonnet = sh.generate_sonnet_syllables(hmm)
new_sonnet, states = sh.generate_rhyming_sonnet(hmm, rhymes)
for line in new_sonnet:
    print(line)

print('\n')

#print(states)

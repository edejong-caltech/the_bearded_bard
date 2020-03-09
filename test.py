import sonnet_helper as sh
from HMM import unsupervised_HMM

sonnets = sh.load_sonnet_text('shakespeare.txt')
dictionary = sh.get_dictionary(sonnets)
rhymes = sh.get_rhymes(sonnets)
seqs = sh.sonnets_to_seqs(sonnets)

N_states = 10 # can be changed
N_iters = 1 # can be changed

hmm = unsupervised_HMM(seqs, N_states, dictionary, N_iters)
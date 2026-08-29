# start: every character is a token
#   l o w e r   n e w e s t   w i d e s t

# merge the most frequent pair, repeatedly:
#   "e" + "s" -> "es"        n e w es t   w i d es t
#   "es" + "t" -> "est"      n e w est    w i d est
#   "l" + "o"  -> "lo"       lo w e r

# stop when the vocabulary reaches the target size

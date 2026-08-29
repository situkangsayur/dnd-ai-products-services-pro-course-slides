# 1. Bernilai kecil - umumnya di rentang 0-1
# 2. Homogen - semua fitur kira-kira
#    dalam rentang yang sama

# praktik yang lebih ketat, sering
# menolong walau tidak selalu perlu:
x -= x.mean(axis=0)   # rerata 0
x /= x.std(axis=0)    # simpangan baku 1
# (x = matriks 2D (samples, features))

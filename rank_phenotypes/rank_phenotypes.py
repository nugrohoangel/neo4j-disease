import json, math

# loading disease and phenotype weights
diseases = {}
with open('weights_disease.json') as f:
    diseases = json.load(f)
    print('%d disease weights loaded!' % len(diseases))

phenotypes = {}
with open('weights_phenotype.json') as f:
    phenotypes = json.load(f)
    print('%d phenotype weights loaded!' % len(phenotypes))


def rank_phenotypes_weighted_tfidf2(phenos):
    print('ranking diseases for phenotypes\n...%s' % phenos)
    # iterate through each disease and calculate the tf-idf for the given
    # phenotypes
    rank = []
    N = len(diseases)
    for did, disease in diseases.items():
        p1 = set(phenos)
        #p2 = set(disease['phenotypes'])
        p2 = set(disease['phenotypes'].keys())
        p3 = p1 & p2 # intersection
        if len(p3) > 0:
            # calculate tf-idf
            tf = 0
            nd = 0
            for p in p3:
                tf += phenotypes[p]['weight']
                nd += len(phenotypes[p]['diseases'])

            if nd > 0: # should always be the case!
                # normalize by total weight for this disease
                tf /= disease['phenowt']
                # tf is regulated by the inverse average phenotype frequency
                rank.append((tf * math.log10(N*len(p3)/nd), disease, p3))
            
    return sorted(rank, key=lambda x: x[0], reverse=True)

def rank_phenotypes_weighted_tfidf(phenos):
    print('ranking diseases for phenotypes\n...%s' % phenos)
    # iterate through each disease and calculate the tf-idf for the given
    # phenotypes
    rank = []
    N = len(diseases)
    for did, disease in diseases.items():
        p1 = set(phenos)
        #p2 = set(disease['phenotypes'])
        p2 = set(disease['phenotypes'].keys())
        p3 = p1 & p2 # intersection
        if len(p3) > 0:
            # calculate tf-idf
            score = 0
            pwt = disease['phenowt']
            for p in p3:
                # penalize phenotypes with high weights
                tf = 1 - phenotypes[p]['weight']/pwt
                idf = math.log10(N/len(phenotypes[p]['diseases']))
                score += tf*idf
            rank.append((score, disease, p3))
            
    return sorted(rank, key=lambda x: x[0], reverse=True)

def rank_phenotypes_tfidf(phenos):
    print('ranking diseases for phenotypes\n...%s' % phenos)
    # iterate through each disease and calculate the tf-idf for the given
    # phenotypes
    rank = []
    N = len(diseases)
    for did, disease in diseases.items():
        p1 = set(phenos)
        #p2 = set(disease['phenotypes'])
        p2 = set(disease['phenotypes'].keys())
        p3 = p1 & p2 # intersection
        if len(p3) > 0:
            # calculate tf-idf
            score = 0
            total = len(disease['phenotypes'])
            for p in p3:
                tf = 1/total
                idf = math.log10(N/len(phenotypes[p]['diseases']))
                score += tf*idf
            #rank.append((score, disease, p3))
            rank.append((score * disease['phenotypes'][p], disease, p3))
            
    return sorted(rank, key=lambda x: x[0], reverse=True)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print('Usage: %s HP...' % sys.argv[0])
        sys.exit(1)

    rank = rank_phenotypes_weighted_tfidf(sys.argv[1:])
    for i, r in enumerate(rank):
        print('%5d: %.05f %s %s %s' % (i, r[0], r[1]['id'], r[1]['name'], r[2]))

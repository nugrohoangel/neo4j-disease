import json, math, logging

logger = logging.getLogger(__name__)

class ZebraRank:
    PHENOTYPES = {}
    
    def __init__(self, diswt_file, phewt_file):
        # loading disease and phenotype weights
        self.diseases = {}
        with open(diswt_file) as f:
            self.diseases = json.load(f)
            for d in self.diseases.values():
                pos = d['id'].index(':')
                prefix = d['id'][:pos]
                id = int(d['id'][pos+1:])
                if prefix == 'GARD':
                    name = d['name'].lower().replace(' ', '-')
                    d['url'] = '%d/%s' % (id, name)
                elif prefix == 'ORPHA':
                    d['url'] = '%d' % id
            logger.debug('%s: %d disease weights loaded!' % (
                diswt_file, len(self.diseases)))

        self.phenotypes = {}
        with open(phewt_file) as f:
            self.phenotypes = json.load(f)
            for key, val in self.phenotypes.items():
                if key not in self.PHENOTYPES:
                    self.PHENOTYPES[key] = val
        logger.debug('%d phenotype weights loaded!' % len(self.phenotypes))


    def rank_phenotypes_weighted_tfidf2(self, phenos):
        print('ranking diseases for phenotypes\n...%s' % phenos)
        # iterate through each disease and calculate the tf-idf for the given
        # phenotypes
        rank = []
        N = len(self.diseases)
        for did, disease in self.diseases.items():
            p1 = set(phenos)
            p2 = set(disease['phenotypes'])
            p3 = p1 & p2 # intersection
            if len(p3) > 0:
                # calculate tf-idf
                tf = 0
                nd = 0
                for p in p3:
                    tf += self.phenotypes[p]['weight']
                    nd += len(self.phenotypes[p]['diseases'])

                if nd > 0: # should always be the case!
                    # normalize by total weight for this disease
                    tf /= disease['phenowt']
                    # tf is regulated by the inverse average phenotype frequency
                    rank.append((tf * math.log10(N*len(p3)/nd), disease, p3))
            
        return sorted(rank, key=lambda x: x[0], reverse=True)

    def rank_phenotypes_weighted_tfidf(self, phenos):
        print('ranking diseases for phenotypes\n...%s' % phenos)
        # iterate through each disease and calculate the tf-idf for the given
        # phenotypes
        rank = []
        N = len(self.diseases)
        for did, disease in self.diseases.items():
            p1 = set(phenos)
            p2 = set(disease['phenotypes'])
            p3 = p1 & p2 # intersection
            if len(p3) > 0:
                # calculate tf-idf
                score = 0
                pwt = disease['phenowt']
                for p in p3:
                    # penalize phenotypes with high weights
                    tf = 1 - self.phenotypes[p]['weight']/pwt
                    idf = math.log10(N/len(self.phenotypes[p]['diseases']))
                    score += tf*idf
                rank.append((score, disease, p3))
            
        return sorted(rank, key=lambda x: x[0], reverse=True)

    def rank_phenotypes_tfidf(self, phenos):
        print('ranking diseases for phenotypes\n...%s' % phenos)
        # iterate through each disease and calculate the tf-idf for the given
        # phenotypes
        rank = []
        N = len(self.diseases)
        for did, disease in self.diseases.items():
            p1 = set(phenos)
            p2 = set(disease['phenotypes'])
            p3 = p1 & p2 # intersection
            if len(p3) > 0:
                # calculate tf-idf
                score = 0
                total = len(disease['phenotypes'])
                for p in p3:
                    tf = 1/total
                    idf = math.log10(N/len(self.phenotypes[p]['diseases']))
                    score += tf*idf
                rank.append((score, disease, p3))
            
        return sorted(rank, key=lambda x: x[0], reverse=True)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print('Usage: %s HP...' % sys.argv[0])
        sys.exit(1)

    zebra = ZebraRank('../weights_disease_S_ORDO_ORPHANET.json',
                      '../weights_phenotype_S_ORDO_ORPHANET.json')
    rank = zebra.rank_phenotypes_weighted_tfidf(sys.argv[1:])
    for i, r in enumerate(rank):
        print('%5d: %.05f %s %s %s' % (i, r[0], r[1]['id'], r[1]['name'], r[2]))

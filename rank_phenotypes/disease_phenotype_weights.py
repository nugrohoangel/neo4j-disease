from neo4j import GraphDatabase
import json

uri = "bolt://disease.ncats.io:80"
driver = GraphDatabase.driver(uri, auth=("neo4j", ""))

def disease_phenotype_weights(tx, weights, prevalences): #added prevalences dict
    diseases = {}
    for d in tx.run("""
match (n:S_GARD)<--(d:DATA)
return id(n) as id, d.gard_id as `dis_id`, d.name as `name`"""):
        node = int(d['id']) # internal node id
        id = d['dis_id']
        disease = {
            'id': id,
            'node': node,
            'name': d['name'],
            'phenotypes': {}
        }
        if node in weights:
            disease['weight'] = weights[node]

        diseases[id] = disease

    phenotypes = {}
    remove = []
    for did, disease in diseases.items():
        phenowt = 0
        for p in tx.run("""
match (n:S_GARD)-[:R_rel{name:'has_phenotype'}]->(m:S_HP)<--(d:DATA)
where id(n) = {id}
return id(m) as id, d.notation as `hp_id`, d.label as `name`""",
                        id=disease['node']):
            node = int(p['id'])
            id = p['hp_id']
            wt = 0
            if node in weights:
                wt = weights[node]
            if id not in phenotypes:
                pheno = {
                    'id': id,
                    'node': node,                    
                    'name': p['name'],
                    'diseases': [did]
                }
                if node in weights:
                    pheno['weight'] = wt
                phenotypes[id] = pheno
            else:
                phenotypes[id]['diseases'].append(did)
            phenowt += wt
            #disease['phenotypes'].append(id)
            x = prevalences[disease['id']][id]
            disease['phenotypes'][id] = x
            
        if len(disease['phenotypes']) == 0:
            remove.append(did)
        else:
            diseases[did]['phenowt'] = phenowt
            #disease['phenotypes'].sort()
            print(disease)

    for pip, phenotype in phenotypes.items():
        diswt = 0
        for did in phenotype['diseases']:
            diswt += diseases[did]['weight']
        phenotype['diseases'].sort()
        phenotype['diswt'] = diswt
    
    # remove diseases with no phenotypes
    for did in remove:
        del(diseases[did])
        
    return diseases, phenotypes

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('Usage: %s WEIGHT_FILE PREVALENCES_FILE' % sys.argv[0])
        sys.exit(1)
        
    weights = {}
    with open(sys.argv[1]) as f:
        count = 0
        for line in f.readlines():
            id, w = line.strip().split(',')
            if count > 0:
                weights[int(id)] = float(w)
            count += 1
        print ('%d weights loaded!' % len(weights))
        
    prevalences = {}
    with open(sys.argv[2]) as f:
        count = 0
        for line in f.readlines():
            hp_code, prev, gard_code = line.strip().split(',')
            if count > 0:
                if gard_code not in prevalences.keys():
                    prevalences[gard_code] = {}
                
                if "Excluded" in prev:
                    prevalences[gard_code][hp_code] = 0/100
                elif "Very rare" in prev:
                    prevalences[gard_code][hp_code] = 2.5/100
                elif "Occasional" in prev:
                    prevalences[gard_code][hp_code] = 17/100
                elif "Very frequent" in prev:
                    prevalences[gard_code][hp_code] = 89.5/100
                elif "Obligate" in prev: 
                    prevalences[gard_code][hp_code] = 100/100
                else:
                    prevalences[gard_code][hp_code] = 54.5/100                    
                 
            count += 1
        print ('%d prevalences loaded!' % len(prevalences))

    with driver.session() as session:
        diseases, phenotypes = session.read_transaction(
            disease_phenotype_weights, weights, prevalences)
        with open('weights_disease.json', 'w') as f:
            print(json.dumps(diseases, indent=2), file=f)
        with open('weights_phenotype.json', 'w') as f:
            print(json.dumps(phenotypes, indent=2), file=f)

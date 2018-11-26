#!/usr/bin/env python

"""Data import and extraction of lemmas, gold, hypo and target output tags for alignment""" 

def get_lemmas_hypo_tags(file):
    content = [i.strip('\n').split('\t') for i in open(file)] 
    lemmas = [i[0] for i in content]
    hypo = [i[1] for i in content]
    tags = [i[2] for i in content]
    return lemmas, hypo, tags 

def get_gold(file):
    content_ground_truth = [i.strip('\n').split('\t') for i in open(file)]
    gold = [i[1] for i in content_ground_truth]
    return gold

def get_errors(hypo, gold):
    error_list = []
    for i in hypo:
        if i not in gold:
            error_list.append(i)
    return error_list
            
def index_items(hypo, lemmas, gold, tags):
    index_list = range(1, len(hypo) + 1)
    zipped_hypo = list(zip(index_list, hypo))
    zipped_lemmas = list(zip(index_list, lemmas))
    zipped_gold = list(zip(index_list, gold))
    zipped_tags = list(zip(index_list, tags))
    return zipped_hypo, zipped_lemmas, zipped_gold, zipped_tags

def get_indexed_results(error_list, zipped_hypo, zipped_lemmas, zipped_gold, zipped_tags):
    results_list = []
    for i in error_list:
        for w in zipped_hypo:
            for y, x in [w]:
                if i == x:
                    results_list.append(w)
    lemmas_results_list = [] 
    gold_results_list = []
    tags_results_list = []
    for i in results_list:
        for y in zipped_lemmas:
            if i[0] == y[0]:
                lemmas_results_list.append(y[1])
    for i in results_list:
        for y in zipped_gold:
            if i[0] == y[0]:
                gold_results_list.append(y[1])
    for i in results_list:
        for y in zipped_tags:
            if i[0] == y[0]:
                tags_results_list.append(y[1])
    lemma_gold_hypo_tags_list = list(zip(lemmas_results_list, gold_results_list, error_list, tags_results_list))
    return lemma_gold_hypo_tags_list

def main():
    lemmas, hypo, tags = get_lemmas_hypo_tags('finnish-high-out')
    gold = get_gold('finnish-uncovered-test')
    error_list = get_errors(hypo, gold)
    zipped_hypo, zipped_lemmas, zipped_gold, zipped_tags = index_items(hypo, lemmas, gold, tags)
    lemma_gold_hypo_tags_list = get_indexed_results(error_list, zipped_hypo, zipped_lemmas, zipped_gold, zipped_tags)
    columns = ['lemma', 'gold', 'hypo', 'target tag']
    with open('lithuanian_output.tsv', 'w', newline = '') as file:
        output = csv.writer(file, delimiter = '\t')
        output.writerow(columns)
        for lemma, gold, hypo, tags in lemma_gold_hypo_tags_list:
            output.writerow([lemma, gold, hypo, tags])
    
if __name__ == '__main__':
    main()

# Reference link: https://stackoverflow.com/questions/29895602/how-to-save-output-from-python-like-tsv
# Reference link: https://stackoverflow.com/questions/49118619/outputting-a-list-to-a-tsv-file-in-python

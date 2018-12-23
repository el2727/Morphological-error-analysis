#!/usr/bin/env python

import pynini

def get_data(file):
    
    """Read in data from SIGMORPHON Shared Task 2017 for Russian verbs' inflection in first-person singular future tense"""
    
    content = [i.strip('\n').split('\t') for i in open(file)] 
    
    # Get lists of imperfective and perfective verbs

    imperfective_verbs = []
    perfective_verbs = []
    for i in content:
        if 'буду' in i[1]:
            imperfective_verbs.append(i)
        else:
            perfective_verbs.append(i)
    
    return imperfective_verbs, perfective_verbs

# Full list of verbs with prefixes is in the Appendix

def get_percentage_prefix():
    
    """Find out how many verbs start with perfective prefixes"""
    
    # Define perfective prefixes (according to Wade, 2010, 272)
    perfective_prefixes = ['без', 'вз', 'взо', 'во', 'воз', 'вы', 'за', 'из', 'изо', 'на', 'над', 'надо', 'недо', 'низ', 'низо', 
                       'о', 'об', 'обо', 'от', 'ото', 'пере', 'по', 'под', 'подо', 'пона', 'пре', 'пред', 'при', 'про',
                       'раз', 'разо', 'с', 'со', 'у']

    
    prefixed_perfectives = []
    for i in perfective_verbs:
        for y in perfective_prefixes:
            if i[0].startswith(y):
                prefixed_perfectives.append(i[0])
                
    prefixed_perfectives_cleaned = set(prefixed_perfectives)
    percentage_prefix_perfective = len(prefixed_perfectives_cleaned)/len(perfective_verbs)
   
    prefixed_imperfectives = []
    for i in imperfective_verbs:
        for y in perfective_prefixes:
            if i[0].startswith(y):
                prefixed_imperfectives.append(i[0])
            
    prefixed_imperfectives_cleaned = set(prefixed_imperfectives)
    percentage_prefix_imperfective = len(prefixed_imperfectives_cleaned)/len(imperfective_verbs)
    
    return print("Percentage of perfective prefixes in perfective verbs:", percentage_prefix_perfective,
                 "Percentage of perfective prefixes in imperfective verbs:", percentage_prefix_imperfective)


def future_perfective(stem):
    
    """Transducer for first-person singular future tense of perfective verbs""" 
    
    vowels = pynini.union("а", "е", "ё", "и", "о", "у", "ы", "э", "ю", "я")
    yer = pynini.union("ь", "ъ") 
    consonants = pynini.union("б", "в", "г", "д", "ж", "з", "й", "к", "л", "м", "н", "п", "р", "с", "т", "ф", "х", "ц", "ч", "ш", "щ")
    sigma_star = pynini.union(vowels, consonants, yer).closure()
    future_tense_map = pynini.union(
                    #Consonant mutation cases as mentioned in Wade, 2010
                    # т : ч
                    pynini.cdrewrite(pynini.t("тать", "чу"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("тить", "чу"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("теть", "чу"), "", "", sigma_star) *
                    # д : ж
                    pynini.cdrewrite(pynini.t("деться", "жусь"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("дить", "жу"), "", "", sigma_star) *
                    # в : вл
                    pynini.cdrewrite(pynini.t("вить", "влю"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("виться", "влюсь"), "", "", sigma_star) *
                    # c : ш
                    pynini.cdrewrite(pynini.t("саться", "шусь"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("сить", "шу"), "", "", sigma_star) *
                    # м : мл
                    pynini.cdrewrite(pynini.t("мить", "млю"), "", "", sigma_star) *
                    # б : бл
                    pynini.cdrewrite(pynini.t("бить", "блю"), "", "", sigma_star) *
                    # п : пл
                    pynini.cdrewrite(pynini.t("пать", "плю"), "", "", sigma_star) *
        
                    #Consonant mutation cases not mentioned in Wade, 2010
                    # ч : к (Wade, 2010 к : ч)
                    pynini.cdrewrite(pynini.t("речь", "реку"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("чься", "кусь"), "", "", sigma_star) *
                    # ч : г
                    pynini.cdrewrite(pynini.t("ечь", "ягу"), "", "", sigma_star) *
                    # х : д
                    pynini.cdrewrite(pynini.t("хать", "ду"), "", "", sigma_star) *
                    # c : д
                    pynini.cdrewrite(pynini.t("сть", "ду"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("стить", "щу"), "", "", sigma_star) *
                    
                    #First singular form of future with ю
                    pynini.cdrewrite(pynini.t("ить", "ю"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("тать", "таю"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("ртеть", "ртею"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("мыть", "мою"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("еть", "ею"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("ртеть", "ртею"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("лать", "лаю"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("питать", "питаю"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("меть", "мею"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("лоть", "лю"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("отлить", "отолью"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("ли", "лю"), "", "", sigma_star) *
                    # Mutation with a soft sign
                    pynini.cdrewrite(pynini.t("шить", "шью"), "", "", sigma_star) *
                    
                    #Spelling rule: у instead of ю after sibilants ж, ч, ш, щ           
                    pynini.cdrewrite(pynini.t("щи", "щу"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("жить", "жу"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("зить", "жу"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("чить", "чу"), "", "", sigma_star) *
                   
                    #Future with reflexive suffix
                    pynini.cdrewrite(pynini.t("ся", "сь"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("иться", "юсь"), "", "", sigma_star) *
                    pynini.cdrewrite(pynini.t("аться", "усь"), "", "", sigma_star) *
                   
                    #Stem change (vowel deletion)
                    pynini.cdrewrite(pynini.t("тереть", "тру"), "", "", sigma_star) *
                    
                    #Verbs ending in -дать form future with -м
                    pynini.cdrewrite(pynini.t("дать", "дам"), "", "", sigma_star) *
                   
                    #Deletion of two last letters in the infinitive stem
                    pynini.cdrewrite(pynini.t("ть", ""), "", "", sigma_star),
                   ).optimize()
    
    return (stem * future_tense_map).stringify()


def evaluation(perfective_verbs):
    perfective_verbs_test = []
    for i in perfective_verbs[62:]:
        perfective_verbs_test.append(i[0])
    
    results = []
    for i in perfective_verbs_test:
        results.append(future_perfective(i))
        
    correct_list = []
    for i in perfective_verbs[62:]:
        for y in results:
            if y == i[1]:
                correct_list.append(y)
                
    accuracy = len(correct_list)/len(results)
    return accuracy

def main():
    imperfective_verbs, perfective_verbs = get_data('verbs_future_forms_first_sg')
    get_percentage_prefix()
    accuracy = evaluation(perfective_verbs)
    print("Transducer accuracy:", accuracy)

if __name__ == '__main__':
    main()

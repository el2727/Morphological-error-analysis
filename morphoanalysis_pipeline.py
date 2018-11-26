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

"""Three-way alignment for morphological error analysis.
DESCRIPTION TO FOLLOW."""

# If there are many optimal alignments we're going to select one randomly.
# This is just for stability.

SEED = 1917
import string
import collections
import pynini

SEP_CHAR = "+"
SEP_CODE = ord(SEP_CHAR)

def _edit_transducer():
    """Builds single-factor edit transducer.
    Should probably ve modified to use two-factor construction here:
        https://github.com/kylebgorman/EditTransducer
    """

    # Matches any printable ASCII character with no cost.
    # TODO(kbg,el): We will probably want to do this in UTF-8 mode,
    # and for whatever characters are needed for the script.

    alphabet = string.ascii_letters + SEP_CHAR
    match = pynini.union(*alphabet).optimize()

    # Inserts any lowercase ASCII character with cost one.

    insert = pynini.arcmap(match, map_type="input_epsilon")
    insert.set_final(1, 1)

    # Deletes any lowercase ASCII character with cost one.

    delete = pynini.invert(insert)

    # TODO(kbg,el): We probably want substitution here, too.
    # Combines them into a single edit transducer.

    edit = pynini.union(match, insert, delete).optimize(True).closure()

    return edit.optimize(True)


def _align(i, edit, o):
    """Computes label alignment."""

    lattice = i @ edit @ o
    # TODO(kbg,el): Make a better error handler.
    if lattice.start() == pynini.NO_STATE_ID:
        raise ValueError("Composition failure")

    # Removes non-optimal paths.
    lattice.prune(weight=0)

    # Randomly samples a path in case there are ties.
    path = pynini.randgen(lattice, seed=SEED).paths()
    return (path.ilabels(), path.olabels())

def segment(lemma, edit, inflected):
    """Inserts "+" prefix-stem and stem-suffix boundaries."""

    (ilabels, olabels) = _align(lemma, edit, inflected)

    # Compute prefix-stem boundary (may be 0).

    for (i, ilabel) in enumerate(ilabels):
        if ilabel != 0:
            break

    prefix_stem = i
    # TODO(kbg,el): There has to be a better way.
    for (i, ilabel) in reversed(list(enumerate(ilabels))):
        if ilabel != 0:
            break

    stem_suffix = i
    return (
        inflected[:prefix_stem]
        + SEP_CHAR
        + inflected[prefix_stem:stem_suffix]
        + SEP_CHAR
        + inflected[stem_suffix:]
    )

# Named tuple for fields returned by next function.

_MorphErrors = collections.namedtuple(
    "MorphErrors", ("prefix", "stem", "suffix")
)

def errors(gold_segmented, edit, hypo):
    """Codes errors in prefix, stem, and suffix."""
    (ilabels, olabels) = _align(gold_segmented, edit, hypo)

    # Errors in prefix, stem, and suffix. `error_id` points to whichever we are
    # reading at the present moment.

    errors = [False, False, False]
    error_id = 0

    for (i, o) in zip(ilabels, olabels):
        if i == SEP_CODE:
            error_id += 1
        elif i != o:
            errors[error_id] = True
    return _MorphErrors(*errors)

edit = _edit_transducer()

# Actual example, from German.

# First we compute the segmentation using the gold as reference,

# then we compare the segmented gold to the hypothesis.

lemma = "singen"  # Infinitive
gold = "gesungen"  # Past participle.
gold_segmented = segment(lemma, edit, gold)
assert gold_segmented == "ge+sungen+"

# A silly hypothesis (but what I was thinking it was earlier today):
# a strong verb but with the wrong ablaut grade.

hypo = "gesangen"  # *.
codes = errors(gold_segmented, edit, hypo)
assert not codes.prefix
assert codes.stem  # Wrong ablaut grade.
assert not codes.suffix

# Another silly hypothesis: as if it were a weak verb.
hypo = "gesingt"  # *.
codes = errors(gold_segmented, edit, hypo)
assert not codes.prefix
assert codes.stem  # No ablaut.
assert codes.suffix  # Wrong suffix.

# The answer.
hypo = "gesungen"
codes = errors(gold_segmented, edit, hypo)
assert not codes.prefix
assert not codes.stem
assert not codes.suffix


"""Do we loop over results here?"""

for a, b, c, d in lemma_gold_hypo_tags_list:
    gold_segmented = segment(a, edit, b)
    codes = errors(gold_segmented, edit, c)
    error_types = [bool(i) for i in codes]

len(error_types)

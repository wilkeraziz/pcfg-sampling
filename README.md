# pcfg-sampling
Sampling algorithms for PCFGs

# PCFG parser


    echo 'I was given a million dollars .' | python parse.py examples/wsj00 --grammarfmt discodop -v --samples 10


To deal with unknown words you need to choose a model (check options with `--help`):


    echo 'I was given a million euros .' | python parse.py examples/wsj00 --grammarfmt discodop --unkmodel stfd6 -v --samples 10


# ITG parser

    echo '1 2 3 4' | python itg-parse.py examples/itg


For small examples, we can list the permutations

    echo '1 2 3 4' | python itg-parse.py examples/itg --show-permutations

# Binarizable permutations

    echo '1 2 3 4' | python binarizable.py

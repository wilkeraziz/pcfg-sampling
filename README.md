# pcfg-sampling
Sampling algorithms for PCFGs

# PCFG parser


    echo 'I was given a million dollars .' | python parse.py examples/wsj00 --grammarfmt discodop --unkmodel stfd6 -v --samples 100 --intersection nederhof --start TOP --log > nederhof.mc

Or

    echo 'I was given a million dollars .' | python parse.py examples/wsj00 --grammarfmt discodop --unkmodel stfd6 -v --samples 100 --intersection earley --start TOP --log > examples/earley.mc


# ITG parser

    echo '1 2 3 4' | python itg-parse.py examples/itg


For small examples, we can list the permutations

    echo '1 2 3 4' | python itg-parse.py examples/itg --show-permutations

# Binarizable permutations

    echo '1 2 3 4' | python binarizable.py

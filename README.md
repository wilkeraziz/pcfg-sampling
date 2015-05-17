# pcfg-sampling
Sampling algorithms for PCFGs

# PCFG parser

    
    echo '1 2 3 4' | python parse.py examples/itg


# ITG parser

    echo '1 2 3 4' | python itg-parse.py examples/itg


For small examples, we can list the permutations

    echo '1 2 3 4' | python itg-parse.py examples/itg --show-permutations

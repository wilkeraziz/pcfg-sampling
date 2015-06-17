# Experiments with the reordering grammar


## MC


            head -n1 data/input/input_11-20.696 | python parse.py $GRAMMAR --grammarfmt milos --start ROOT --default-symbol UNK --unkmodel passthrough --log --split-input --samples 100 --profile mcmc_pstats > output


## MCMC



            head -n1 data/input/input_11-20.696 | python mcmcparse.py $GRAMMAR --grammarfmt milos --start ROOT --default-symbol UNK --unkmodel passthrough --log --split-input --samples 100 --profile mcmc_pstats > output

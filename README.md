# blockchain oracle

## Intro
This program is a proof-of-concept for a secure decentralized voting PSCBO (our proposal in the directory "secureVote") and an insecure one (in the directory "vote"). Significantly, this program is at an infant stage just for experimentation.
## Structure
### The explanation
#### Beacon.py
We introduce Beacon.py as a trusted slot leader selector, besides we input the data check functionality "V" here.
#### Algorithm.py
We implement the basic algorithm here, including generating blocks, verifying blocks, and so on.
#### Votereliabe.py
Our main and the outermost code is executed to generate a blockchain.
### ToVote
Respectively, in the SecureVote and Vote directory, execute Votereliabe.py to generate a secure chain or vote_rbpl.py to get an insecure one. We invoke multiprocess to simulate different consensus nodes. Finally, the analyzer.py will plot the specific chain structure.
### Dara test
To make the experiment feasible, the datatest.py simplifies the experimental process.
### Dara analysis
The directory "Vote_result" records the final data and prints it.

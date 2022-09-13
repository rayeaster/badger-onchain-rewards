from pprint import pprint

from random import seed
from random import random
from copy import deepcopy

"""
  Visualization:
    https://miro.com/app/board/uXjVPfL1y3I=/
  
  Given TokenA -> RewardB -> RewardC

  General Case 2) Random Many to Many some are self-emitting (question is, do we need extra math or not?)

  e.g. (Full)
  From A -> B -> C
         -> B from B -> C from B from B
                   C -> C from C
                   C -> C from C from B from B

This Simulates A -> B -> B'
Where B and B' are not all for the depositors of A

  Token A can be Self-emitting or not (shouldn't matter) - TotalPoints
  (TODO: Math to prove self-emitting is reduceable to this case)

  
  Token B self emits, is also emitted by Vault β and some people hold token B
  - VAULT_B_REWARDS_TO_A
  - VAULT_B_SELF_EMISSIONS
  - VAULT_B_EMISSIONS_TO_OTHER ## Emissions of B for another random vault (Vault β)

  Fix calculation to:
    - Give back "less rewards" directly to direct claimers <- Back to 04 math which is the correct one
    
    Future Rewards Backwards Claims
    - NEW: 
      Reward Positions will claim their rewards when claimed and distribute to users
        Effectively a Reward is a "Virtual Account" meaning just like any user it's accruing rewards
        Because of this, when claiming, we need to claim the rewards that this "Virtual Position" has accrued
        Doing this allows us to never correct the divisor to unfair / overly fair levels, at the cost of computational complexity
        NOTE: At this time  I believe this to be the mathematically correct solution

  - Add non-random version which will help with debugging


  Handle Virtual Accounts along with B -> B' to simulate the "smart contract" claims

  Token C self emits, is also emitted by Vault E and some people hold token C
  - VAULT_C_REWARDS_TO_B
  - VAULT_C_SELF_EMISSIONS
  - VAULT_C_REWARDS_TO_OTHER ## Emissions of C for another random vault (Vault γ)
  - VAULT_C_HODLERS ## NOTE: Removed per cD' -> β explanation

  - Separate the noise / claims into functions
  - Use the functions for A -> B
  - Use the functions for B -> C
  - Add Noise back in

  - TODO: Rewrite all code to use list of tokens to make the random case more complicated
  - TODO Create notation for generalized claiming
  - TODO Solve cross claims math with virtual accounts

  - TODO: Reconcile the vars below to make it so they are used as expected
"""

## Should we use randomness or use just the values provided?
DETERMINISTIC = True

## NOTE: a 1 epoch test MUST always pass
## because the issue of Future Rewards Backwards Claims is not relevant (there is no epoch of unclaimable rewards)
EPOCHS_RANGE = 0  ## Set to 0 to test specific epoch amounts
EPOCHS_MIN = 2

SHARES_DECIMALS = 18
RANGE = 10_000  ## Shares can be from 1 to 10k with SHARES_DECIMALS
MIN_SHARES = 1_000  ## Min shares per user
SECONDS_PER_EPOCH = 604800


### B VARS ###
MIN_VAULT_B_REWARDS_TO_A = (
    500  ## The "true" "base" yield from B -> A (without adding self-emissions)
)
VAULT_B_REWARDS_TO_A = 100_000  ## 100 k ETH example

## B'
VAULT_B_MIN_SELF_EMISSION = 500
VAULT_B_SELF_EMISSIONS = (
    1_000_000  ## 100M ETH example - Exacerbates issue with B -> B Claim
)

## Additional B Rewards (We call them β to separate) <- NOTE: May wanna remove noise for a time
VAULT_B_MIN_REWARDS_TO_OTHER = 0 ## TODO: Add back - Removed to nail down the math of claiming B -> C and C -> C'
VAULT_B_REWARDS_TO_OTHER = 100_000  ## Inflates total supply but is not added to rewards

## NOTE: Unused
## NOTE: See Math to prove we don't need as long as we have `VAULT_B_REWARDS_TO_OTHER`
# VAULT_B_HODLERS = 0


### C VARS ###
VAULT_C_MIN_REWARDS_TO_B = 0  ## 10 k ETH example
VAULT_C_REWARDS_TO_B = 0  ## 100 k ETH example

VAULT_C_MIN_SELF_EMISSIONS = 0  ## TODO: This must be 100% or I made a mistake
VAULT_C_SELF_EMISSIONS = 1_000  ## 1k ETH example

## NOTE: TODO - Zero to make initial sim simpler
## TODO: Add the math as it's not there yet
VAULT_C_MIN_REWARDS_TO_OTHER = 0
VAULT_C_REWARDS_TO_OTHER = (
    0  ## Inflates total supply but is not added to rewards
)



USERS_RANGE = 0
USERS_MIN = 2000


## How many simulations to run?
ROUNDS = 1_000 if not DETERMINISTIC else 1

## Should the print_if_if print_if stuff?
SHOULD_PRINT = ROUNDS == 1


def print_if(v):
    if SHOULD_PRINT:
        print(v)


def get_circulating_supply_at_epoch(total_supply, rewards, emissions, epoch, claim_depth):
    """
        Given the rewards and emissions
        Figure out the circulating supply at that epoch

        `claim_depth`: {enum} - Used to retrieve the divisor that is appropriate to the math
        0 -> Rewards -> Math V1 - total_supply -> Used for All non-emission claims
        1 -> Only Emissions -> Multiple emissions means we need to remove them from the circulating supply

        Ultimately the problem is to figure out circulating_supply, which does change after time

    """

    ## Given depth we'll need to go deeper / less deep
    if claim_depth == 0:
        return total_supply
    
    if claim_depth == 1:
        ## Remove the rewards until this epoch
        ## Remove the emissions until this epoch
        total_emissions_future = emissions[epoch]

        return total_supply - total_emissions_future




## Get total Claimed

## Get Virtual Accounts total Claimed

## Claim from Virtual Accounts as % of total Claimed vs claimable

## If I know how many rewards are locked in contract, and will only be available in the future
## I can claim the emissions from those rewards and use the Ratio to distribute them
# 
# 
# 
#  Reward if A != B
#  Emission if A == B
#  I can always tell if it's an emission or a reward
#  Question is what happens if I can claim from Reward and Emission to new Rewards?


## How do we get Emissions?
## Circulating Supply (- reward_i - emission_i-1) -> And ratio


## How do we get Reward from Reward + Emission?
## Circulating Supply (- reward_i - emission_i) -> And ratio
## Both are i as after the claim they are both circulating


## If No Reward nor emission can be added to future epochs
## Then we have a guarantee that divisor = total_supply for all Rewards
## And divisor = total_supply - points_from_current_emissions for all Emissions

## It follows that for a given Reward of Reward C
## For which B -> B' -> C
## Then receivedC = receivedB + receivedB' / total_supply
## Because a rational actor will claim B -> B' -> C
## Even if they could claim B -> C and loose on some emissions
## Meaning that if an emission is available it must always be claimed first

## Corollary being:
## C1 - A -> B type deal
## If no future tokens (rewards or emissions for future epochs) are present in the contract
## Meaning no extra points are being accrued to the contract but are not claimable then
## Any A -> B type claim will always be divided by B / totalSupply



## Vault -> Reward -> Emission -> Reward -> Emission -> Reward -> Emission -> Reward -> Emission -> Reward -> Emission
"""
A set of claims is basically a path to claims, where the starting point is always Vault
The intermediary steps are the token (and it's emission if available, perhaps packable via `bool`)


    1) A -> B -> B' -> C -> C'
    2) A -> C -> C'
    3) A -> D -> D' -> C -> C'

    Can be resolved as:

    1)
    A -> B
    B -> B'
    B -> C
    C -> C'

    2) 
    A -> C
    C -> C'

    3)
    A -> D
    D -> D'
    D -> C
    C -> C'

A cache of token ratios may help save gas, however ultimately
A "compound claim" is the ordered claim of pair of tokens, accrued to the current epoch


Given Paths 1, 2 and 3
A gas optimized claim would do:
A -> B -> B' -> C
A -> C
A -> D -> D' -> C
C(1 + 2+ 3) -> C'

However it may be impossible to make this replicable for all cases


## NOTE: On Subsegments

X -> A -> *
Z -> A -> *

While this would be mathematically equivalent to
X -> A
Z -> A
A -> *

Because of the function interface starting with one vault, I'll be ignoring that.
If the starting vault is different, just do n claims for each starting node

The sum of all partial claims will be equal to the total claim (minus rounding due to integer division)
"""




"""
    Let Vs = {A, B, ...Z} be the vector of balances

    TVi being Total Supply for Vault V at epoch i === Sum(A)
    vni being balance of user n at epoch i; with vni <= Sum(A)

    R being a generic reward

    Given that all Ri is claimable on each epoch

    Compound Claims Theorem

    For Each V ∈ Vs:
        Claim(V, n, i) ===
        {
            vi / Tvi * Ri; if V != R; Rewards Case
            vi / (Tvi - Ri); if V == R; Emissions Case
        }

    
    Corollary 1 - Definition of Circulating Supply

    Let Tvi being the total Supply for V ∈ Vs at epoch i;

    We define circulating supply (from the Contract POV) as 
    the sum of all Vault shares owned by users, 
    or that are rewards that can be claimed through ownership of a different Vault D ∈ Vs; D != V

    Given V ∈ Vs and TRi as the Sum(Ri) for given epoch i;
    With R == V;

    We separate TRV = TR + TV
    Where TV is circulating and TR are emissions for it

    Because TRV = TR + TV

    We define Circulating supply as TV, the amount of Rewards that are not emissions for the given Vault



    Corollary 2 - Linear Extension

    For Each V ∈ VS; 
    There is no difference if we prove theorems with a vector of one or a vector of n ∈ N

    Proof by absurd:

    Imagine a R as value of rewards and Ri ∈ N; as the specific reward claimable for epoch i

    If Ri is claimable by a single vector N ∈ Vs, then TNi the total supply of N at epoch i maps out to Ri

    If we were to introduce an additional vector M ∈ Vs with 50% of the rewards being equally split between N and M
    Then we would assert that:

    TNi maps out to 50% Ri
    and
    TMi maps out to 50% Ri

    Meaning that for any ni <= TNi; with TNi == SUM(ni); There exist a value r ∈ N; That each share amount can claim

    We can extend this idea to any number of Vaults for any ratio of Rewards.

    Given Vsi and it's subsets and Ri being respectively:
    The permutations of all possible vaults at epoch i and
    The permutation of all possible rewards for each epoch i
    
    With TRi == SUM(Ri) == C * Ri

    Meaning there must be a C ∈ <Q> (Vector of Rational Numbers) that maps out a ratio between TRi and Ri

    If there was no vector, then by absurd, in the case of a single vault 
    The following must be true:
    There is no c ∈ N such that
    TNi == SUM(ni) can claim c * Ri

    This is absurd per the example above
"""


## How do we codify Segments?

"""
    Start
    ClaimDepth
    ClaimTokens1
    ClaimEmissionTokens1
    ...
    ...
    ClaimTokens_ClaimDepth-1
    ClaimEmissionTokens_ClaimDepth-1


    ## What happens if in the middle we have start again?
    ## What happens if we have the same subpath X times?



    RANDOM_CLAIM_DEPTH

    RANDOM_CLAIM_TOKEN_LAYER_1...RANDOM_CLAIM_TOKEN_LAYER_N
    RANDOM_CLAIM_EMISSION_LAYER_1...RANDOM_CLAIM_EMISSION_LAYER_N


    ## What happens if we have the same subpath X times?
    We just recompute it and pay the extra gas, per the logic above it's still the correct math in spite of it wasting gas


    ## What happens if in the middle we have start again?
    Then the entire path is a uber path to start

    N -> A -> M

    Meaning that Start should have been N and not A

    ## NOTE: Worth checking this on Solidity, is uberPath or something, as it's not gas efficient


    ## TODO: What happens on a cross?

    A -> B
    A -> C
    A -> D
    A -> D -> B

    B -> A
    B -> C
    B -> D

    As sum of paths

    A -> D -> B -> A
    A -> D -> B -> C
    A -> D -> B -> D

    In reality

    A -> D -> B -> A
              B -> C
              B -> D
    

    A -> D
    D -> B

    B -> A
    B -> C
    B -> D

    D -> B ??? TODO: This is where problem arise


    ## NOTE: Minimal Problem Statement
    D -> B -> D

    ## RULE: We must revert if you claim the same pair / path twice

    ## What happens if something is a recursive sub path of something else
    ## What math would help?

    (B -> C)*

    B -> C
"""

## Vault / Token Notation | TokenData

"""
    For the purposes of this sim:

    A -> B -> B' -> C -> C'

    Where each of them will have
    {
        ## For each epoch each user. After a claim, increase current
        ## At beginning of new epoch, port over from prev epoch bal
        ## balances[epoch][user] = balances[epoch-1][user]
        balances[epoch][user]: 

        ## How many rewards available this epoch
        rewards[epoch][token]

        ## How many emissions available this epoch (emission = reward for holding vault)
        emissions[epoch]

        ## Sum of balances + rewards + emissions
        total_supply[epoch]: 
    }
"""

def get_start_token_total_supply(users, token_name):
    total_supply = 0

    for user in users:
        user_bal = user.getBalanceAtEpoch("a", 0)
        total_supply += user_bal

    return total_supply


class Token:
    def __init__(self, id, balances, rewards, emissions, total_supply, noise = []):
        self.balances = balances
        self.rewards = rewards
        self.emissions = emissions
        self.total_supply = total_supply
        self.id = id
        self.noise = noise


def create_start(epoch_count, user_count, min_shares, shares_range, decimals, determinsitic):

    ## Start is always a token that is not a reward nor an emission

    balances = []
    rewards = [0]
    emissions = [0]

    ## Cumulative amount that increases by reward on each epoch
    ## 0 -> reward_0
    ## n > reward_n-1 + reward_n
    total_supply = []


    for epoch in range(epoch_count):
        balances.append([])
        total_supply.append(0)
        for user in range(user_count):
            balances[epoch].append(0)

    print("create_start balances", balances)

    for user in range(user_count):
        ## User Balance
        balance = (
            (int(random() * shares_range) + min_shares) * 10**decimals
            if not determinsitic
            else min_shares * 10**decimals
        )
        balances[0][user] = balance

        total_supply[0] += balance
    
    return Token("a", balances, rewards, emissions, total_supply)


def create_reward_token(name, epoch_count, min_reward, reward_range, decimals, determinsitic, with_emission = True):
    ## Reward means no emissions
    ## Add the flip somewhere else
    
    balances = []
    rewards = []
    emissions = [0]
    total_supply = [0]

    ## Balances that are entitled to emissions and not reward
    ## Can just be a single amount per epoch as you can imagine the vector or holders and sum it up to one user
    noise = []

    for epoch in range(epoch_count):
        balances.append([]) ## 0

        noise.append(0)
        rewards.append(0)
        emissions.append(0)
        total_supply.append(0)

    for epoch in range(epoch_count):
        ## Create reward always
        reward = (
            (int(random() * reward_range) + min_reward) * 10**decimals
            if not determinsitic
            else min_reward * 10**decimals
        )
        rewards[epoch] = reward

        ## Port over Total Supply
        ## Also add noise and port it over for all epochs
        if(epoch > 0):
            total_supply[epoch] = total_supply[epoch - 1]
            noise[epoch] = noise[epoch - 1] ## Port over noise from prev as it's cumulative
        else:
            ## If epoch is 0 add the noise
            ## We port it over for math later
            noise_bal = (
                (int(random() * reward_range) + min_reward) * 10**decimals
                if not determinsitic
                else min_reward * 10**decimals
            )
            noise[epoch] = noise_bal
            total_supply[epoch] += noise_bal


        total_supply[epoch] += reward

        if(with_emission):
            ## Emission and reward math is same, TODO: deal with it
            emission = (
                (int(random() * reward_range) + min_reward) * 10**decimals
                if not determinsitic
                else min_reward * 10**decimals
            )
            emissions[epoch] = emission
            
            total_supply[epoch] += emission

    
    return Token(name, balances, rewards, emissions, total_supply, noise)


## ClaimPair Notation
"""
(Vault, Token)

isReward if Vault != Token

isEmission if Vault == Token

This allows us to write the whole claim loop as
do_claim(ClaimPair[], epochStart, epochEnd)

Which will call for i = epochStart; i < epochEnd
do_claim(Vs, ClaimPair[], epoch_i)

Which calls
for n = 0; n < claimPair.length
do_claim(Vs, claimPair_n, epoch_i)

Where Vs is the Virtual State of balances accrued
claimPair[] is the list of all claimPair, all pairs are unique at this time (no crossing)
TODO: Figure out Crossing

Uniqueness of claims
We can track it via claimed[epoch][vault][token]
Which we can sim in Python via
claimed = [keccak(epoch + vault + token)] where + is the string concatenation operator and keccak is SHA256
Verifying uniqueness of claim in python is trivial

Interestingly enough, for gas purposes it may be cheaper to use the same technique in Solidity and then Zero Out all arrays for balances, 
making claims cheaper by deleting your balance.

Downside is if you don't claim exhaustively in one go, you will lose a lot of value potentially

Upside is I think this eliminates one storage slot for all claims so that's pretty huge (20k per epoch)
"""


def get_random_user_start_balance():
    balance = (
        (int(random() * MIN_SHARES) + MIN_SHARES) * 10**SHARES_DECIMALS
        if not DETERMINISTIC
        else MIN_SHARES * 10**SHARES_DECIMALS
    )

    return balance



class UserBalances:
    """
        start_token
        tokens
        epochs

        Just use `getBalanceAtEpoch`
        Which also updates the balance from old epoch
    """
    def __init__(self, start_token, tokens, epochs):
        ## Create empty token balances
        empty_balance = []
        for epoch in range(epochs):
            empty_balance.append(0)
        
        start_token_balance = empty_balance.copy()
        start_token_balance[0] = get_random_user_start_balance()

        setattr(self, start_token, start_token_balance.copy())

        for token in tokens:
            setattr(self, token, empty_balance.copy())

        ## Limit of epochs, just for addBalanceAtEpoch
        self.epochs = epochs
    
    def getBalances(self, token_name):
        return getattr(self, token_name)
    
    def getBalanceAtEpoch(self, token_name, epoch):
        balances = getattr(self, token_name)

        ## Saves us having to port over balances
        ## If > 0 and if not last epoch
        ## NOTE: Assumes we always loop from 0 -> n stepwise, skipping one epoch = break the logic
        if(balances[epoch] == 0 and epoch > 0):
            balances[epoch] = balances[epoch - 1]
            setattr(self, token_name, balances.copy())
        
        return balances[epoch]
    
    def addBalanceAtEpoch(self, token_name, epoch, amount):
        if(epoch > self.epochs):
            return False
        
        ## Lookback + port over balance
        balanceAtEpoch = self.getBalanceAtEpoch(token_name, epoch)
        balanceAtEpoch += amount

        balances = getattr(self, token_name)
        balances[epoch] = balanceAtEpoch

        setattr(self, token_name, balances.copy())


def create_users(epoch_count, user_count, start_token, tokens):
    users = []
    for user in range(user_count):
        new_user = UserBalances(start_token, tokens, epoch_count)
        users.append(new_user)

        print(vars(new_user))
    
    return users

    
class TokenClaimData:
    def __init__(self, token, claim_emission):
        self.token = token
        self.claim_emission = claim_emission

class ClaimData:
    def __init__(self, tokenClaimDatas: TokenClaimData, next):
        self.data = tokenClaimDatas
        self.next = next

def create_claim_sequence():
    ## TODO: rewrite

    ## For now just return A -> B -> B' -> C -> C'
    a = TokenClaimData("a", False)

    ## Declare C with Emissions
    c = TokenClaimData("c", True)

    ## Declare B with emissions
    b = TokenClaimData("b", True)

    ## A claims B, which claims C
    a_data = ClaimData([a], ClaimData([b], ClaimData([c], None)))

    return a_data

## Validate claimSequence

"""
    Loop over the sequence

    Next.rewards[0][token] MUST be non-zero.

    In Solidity we won't be perfoming the check

    A subsequence zero epoch is acceptable, but first one needs to be non-zero
"""

def is_valid_sequence(vault, path):
    tokens_found = []

    ## Ensure we are starting with vault
    assert path.data[0].token == vault

    while path.next != None:
        path = path.next

        data = path.data

        for entry in data:
            assert entry.token not in tokens_found
            tokens_found.append(entry.token)


## Claim Math

"""
    ## From Claim proof
        For Each V ∈ Vs:
        Claim(V, n, i) ===
        {
            vi / Tvi * Ri; if V != R; Rewards Case
            vi / (Tvi - Ri); if V == R; Emissions Case
        }
"""

def get_reward(balance, total_supply, rewards):
    """
        Use it to receive A -> B type rewards
        Where A != B

        Returns (claimed, dust)
    """

    ## TODO: Do we need rewards[epoch][token] or not? Multi claim / Branchful claims
    divisor = total_supply

    print("balance", balance)
    print("rewards", rewards)
    print("divisor", divisor)

    claimed = balance * rewards // divisor
    dust = balance * rewards % divisor

    return (claimed, dust)

def get_emission(balance, total_supply, emissions):
    """
        Given an (updated e.g already claimed reward) balance, claim the emissions for this epoch

        Use it to receive B -> B' type rewards
        Where B == B' they are the same token

        Returns (claimed, dust)
    """
    ## Any older emission is assumed to be claimed
    ## Because we assume nothing from the future is in, we can just subtract the one from the current claim
    divisor = total_supply - emissions

    claimed = balance * emissions // divisor
    dust = balance * emissions % divisor

    return (claimed, dust)

## Fairness Check at end

"""
    User Deposited / TotalSupply = Expected %


    Recursive validation via:
    -> Expected %
    -> Vs realized %

    NOTE: Can do this because we prove that claiming every week vs once per year is equivalent
    ## As our divisor is not relative to the value
"""

def fairness_check(user_count, epoch_count, balances, total_supply, received_rewards, total_rewards, received_emissions, total_emissions):

    for user in range(user_count):
        for epoch in range(epoch_count):
            check_fair_received(balances[epoch][user], total_supply, received_rewards[epoch], total_rewards[epoch], received_emissions[epoch], total_emissions[epoch])

    ## TODO: Sum it all up

    ## Is the sum of all tokens fair as well?


def check_fair_received(balance, total_supply, received_reward, total_rewards, received_emission, total_emissions):

    expected_percent = balance / total_supply

    ## TODO: Change to allow dust
    assert total_rewards / received_reward == expected_percent
    assert received_emission / total_emissions == expected_percent

    ## Maybe just check on sum, although I think it will always need to be the correct ratio


def main():
    seq = create_claim_sequence()

    ## NOTE: Tested to work
    is_valid_sequence("a", seq)

    epoch_count = 3
    user_count = 3
    min_shares = MIN_SHARES
    shares_range = MIN_SHARES ## TODO
    decimals = SHARES_DECIMALS
    determinsitic = True

    users = create_users(epoch_count, user_count, "a", ["b", "c"])
    start_token_total_supply = get_start_token_total_supply(users, "a")

    b_token = create_reward_token("b", epoch_count, min_shares, shares_range, decimals, determinsitic)
    c_token = create_reward_token("c", epoch_count, min_shares, shares_range, decimals, determinsitic)
    
    pprint(vars(b_token))
    pprint(vars(c_token))
    
    ## TODO: Continue

    ## A -> B -> B'

    for epoch in range(epoch_count):
        print("Epoch", epoch)

        total_rewards_b = 0
        total_emissions_b = 0

        total_rewards_c = 0
        total_emissions_c = 0

        for user in range(user_count):
            print("User Ratio")
            print(users[user].getBalanceAtEpoch("a", epoch) / start_token_total_supply)

            print('users[user].getBalanceAtEpoch("a", 0)', users[user].getBalanceAtEpoch("a", epoch))
            
            (gained_b, dust_b) = get_reward(users[user].getBalanceAtEpoch("a", epoch), start_token_total_supply, b_token.rewards[epoch])
            print("Gained B ratio")
            print(gained_b / b_token.rewards[epoch])

            users[user].addBalanceAtEpoch("b", epoch, gained_b)

            (gained_b_emission, dust_b_emission) = get_emission(users[user].getBalanceAtEpoch("b", epoch), b_token.total_supply[epoch], b_token.emissions[epoch])

            ## Update user Balance for B with B'
            users[user].addBalanceAtEpoch("b", epoch, gained_b_emission)

            print("Gained B Emissions Ratio")
            print(gained_b_emission / b_token.emissions[epoch])


            total_rewards_b += gained_b
            total_emissions_b += gained_b_emission


            (gained_c, dust_c) = get_reward(users[user].getBalanceAtEpoch("b", epoch), b_token.total_supply[epoch], c_token.rewards[epoch])

            ## Port over C balance
            users[user].addBalanceAtEpoch("c", epoch, gained_c)
            
            (gained_c_emission, dust_c_emission) = get_emission(users[user].getBalanceAtEpoch("c", epoch), c_token.total_supply[epoch], c_token.emissions[epoch])

            ## Port over C balance after C'
            users[user].addBalanceAtEpoch("c", epoch, gained_c_emission)

            total_rewards_c += gained_c
            total_emissions_c += gained_c_emission


        ### ==== NOISE ==== ###
        ## Once Per Epoch we also account for the noise
        ## NOTE: Added Noise Claim for Current Token
        (gained_b_emission_from_noise, dust_b_emission_from_noise) = get_emission(b_token.noise[epoch], b_token.total_supply[epoch], b_token.emissions[epoch])
        ## Update current for below
        b_token.noise[epoch] += gained_b_emission_from_noise

        if epoch + 1 < epoch_count:
            ## Port over old balance as well
            b_token.noise[epoch + 1] = b_token.noise[epoch]
        
        total_emissions_b += gained_b_emission_from_noise



        ## TODO: Holder of B also needs to receive C
        (gained_c_rewards_from_noise, dust_c_rewards_from_noise) = get_reward(b_token.noise[epoch], b_token.total_supply[epoch], c_token.emissions[epoch])

        ## Update current for below
        c_token.noise[epoch] += gained_c_rewards_from_noise

        if epoch + 1 < epoch_count:
            ## Port over old balance as well
            c_token.noise[epoch + 1] = c_token.noise[epoch]
        
        total_rewards_c += gained_c_rewards_from_noise



        ## NOTE: Added Noise Claim for C Token
        (gained_c_emission_from_noise, dust_c_emission_from_noise) = get_emission(c_token.noise[epoch], c_token.total_supply[epoch], c_token.emissions[epoch])

        ## Update current for below
        c_token.noise[epoch] += gained_c_emission_from_noise

        if epoch + 1 < epoch_count:
            c_token.noise[epoch + 1] = c_token.noise[epoch]
        
        total_emissions_c += gained_c_emission_from_noise

        
        ## End of epoch recap 
        ## TODO: Refactor to capture individual and total claims
        ## TODO: Use that to generalize claim fairness math
        print("Fairness / Distribution Ratio for Epoch", epoch)
        rewards_ratio_b = total_rewards_b / b_token.rewards[epoch]
        b_emissions_ratio_b = total_emissions_b / b_token.emissions[epoch]
        print(rewards_ratio_b)
        print(b_emissions_ratio_b)

        assert rewards_ratio_b == 1
        assert b_emissions_ratio_b == 1


        print("Fairness / Distribution Ratio for Epoch for C", epoch)
        rewards_ratio_c = total_rewards_c / c_token.rewards[epoch]
        emissions_ratio_c = total_emissions_c / c_token.emissions[epoch]
        print(rewards_ratio_c)
        print(emissions_ratio_c)

        assert rewards_ratio_c == 1
        assert emissions_ratio_c == 1
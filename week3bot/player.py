'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction, BidAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import random
import eval7
import math
from itertools import combinations

#section on building all hands
def generate_deck():
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    suits = ['h', 'd', 'c', 's']
    deck = [rank + suit for rank in ranks for suit in suits]
    return deck

def generate_all_hands(deck, number):
    combos = list(combinations(deck, number))
    return ["".join(c) for c in combos]
#
def calculate_hand_equity(hand, board):
    deck = generate_deck()
    remaining_deck = [card for card in deck if card not in hand and card not in board]
    wins = 0
    iterations = 100  

    for _ in range(iterations):
        random.shuffle(remaining_deck)
        opponent_hand = remaining_deck[:2]
        future_board = board + remaining_deck[2:7-len(board)]
        my_score = eval7.evaluate([eval7.Card(card) for card in hand + future_board])
        opponent_score = eval7.evaluate([eval7.Card(card) for card in opponent_hand + future_board])
        if my_score > opponent_score:
            wins += 1
    print(wins/iterations)
    return wins / iterations

equity_multipliers = {
    'consistent_hand': 1.5,
    'likely_loss': .25,
    'won_bid': 1.3,
    'improved_equity': 1.3
}

hand_to_equity = {
    "High Card": 0.2,
    "Pair": 0.4,
    "Two Pair": 0.8,
    "Trips": 0.95,
    "Straight": 0.98,
    "Flush": 1,
    "Full House": 1,
    "Quads": 1,
    "Straight Flush": 1,
    "Royal Flush": 1
}

equity_multipliers = {
    'consistent_hand': 1.5,
    'likely_loss': .25,
    'won_bid': 1.3,
    'improved_equity': 1.3
}

pocket_2_max, pocket_2_min = 17563648, 327680

deck = generate_deck()

all_hands_2_str = generate_all_hands(deck,2)
all_hands_2 = [[eval7.Card(hand[:2]) , eval7.Card(hand[2:])] for hand in all_hands_2_str]
all_hands_3_str = generate_all_hands(deck,3)
all_hands_3 = [[eval7.Card(hand[:2]) , eval7.Card(hand[2:])] for hand in all_hands_3_str]

pre_flop_fold = []
for hand in all_hands_2:
    if hand[0].suit != hand[1].suit and hand[0].rank != hand[1].rank and (hand[0].rank + hand[1].rank < 10):
        pre_flop_fold.append(hand)
#pre_flop_fold = [[eval7.Card(hand[:2]) , eval7.Card(hand[2:])] for hand in pre_flop_fold]
great_preflop = []
for h in all_hands_2:
    if ((h[0].rank == h[1].rank and h[0].rank + h[1].rank >= 14) or h[0].rank + h[1].rank >= 22):
        great_preflop.append(h)
class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        pass

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        my_cards = previous_state.hands[active]  # your cards
        opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        pass

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        # May be useful, but you may choose to not use.
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        my_bid = round_state.bids[active]  # How much you bid previously (available only after auction)
        opp_bid = round_state.bids[1-active]  # How much opponent bid previously (available only after auction)
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        pot = my_contribution + opp_contribution
        big_blind = bool(active)
        if RaiseAction in legal_actions:
           min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
           min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
           max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
           #print(min_raise, max_raise, my_stack, opp_stack, my_pip, opp_pip)

        def bail_option(legal_actions):
            if CheckAction in legal_actions:
                return CheckAction()
            return FoldAction()
    
        #___myLogic___
        all_cards = my_cards + board_cards
        hand = [eval7.Card(s) for s in all_cards]
        hand_rank = eval7.evaluate(hand)
        hand_type = eval7.handtype(hand_rank)
        #equity = hand_to_equity[hand_type]
        equity = calculate_hand_equity([card for card in my_cards], [card for card in board_cards])

        if BidAction in legal_actions:
            boldness = 1  #boldness is an adjustment for all of our bid amounts
           
             #checks for pocket pair          
            
            if my_cards[0][0] == my_cards[1][0]:
                ranks = []
                for c in board_cards:
                    if c[0] not in ranks:
                        ranks.append(c[0])
                if len(ranks) <=2:
                    bidamount = min(int(my_stack*.75), int(.75*pot))
                    return BidAction(bidamount) #if we have pocket pair and a paired board, we will bet more in hopes of a full house or quads
                else:
                    return BidAction(int(.2 * my_stack * boldness)) #if we just have a pair another card would be helpfull, but our odds of flush or better are lower, so the card is worth less
           
                    
            elif my_cards[0][1] == my_cards[1][1]:  #flush draw scenario
                suits = []
                for c in board_cards:
                    
                    if c[1] in suits:
                        preferred = c[1]
                    if c[1] not in suits:
                        suits.append(c[1])
                    
                if len(suits) <= 2 and preferred == my_cards[0][1]:
                    return BidAction(int(.3 * my_stack * boldness)) #if we have 4 cards of the same suit, we will bid bigger in hopes of a flush
                    


            
            return BidAction(my_stack/2)
        
        #preflop logic
        initial_equity = equity
        if not big_blind and len(board_cards)==0: #we are small blind
                
            #print(hand)
            if hand in great_preflop:
                if RaiseAction in legal_actions:
                    return RaiseAction(min(int(4*opp_pip), max_raise))
            elif hand in pre_flop_fold:
                return FoldAction()
            else:
                if CheckAction in legal_actions:
                    return CheckAction()
            if hand in pre_flop_fold:
                print('hand should be folded')
                if CheckAction in legal_actions:
                    return CheckAction()
                return FoldAction()
            else:
                if eval7.evaluate(hand) > 0.9 * pocket_2_max:
                    if RaiseAction in legal_actions:
                        return RaiseAction(max_raise)
                
                if hand in pre_flop_fold:
                    if CheckAction in legal_actions:
                        return CheckAction()
                    return FoldAction()
                elif hand in great_preflop and RaiseAction in legal_actions:
                    #return RaiseAction(min(int(3.2*opp_pip), max_raise))
                     #this creates the error for illegal raise
                    raiseamount = min(max_raise-1, 3.2*opp_pip)
                    return RaiseAction(raiseamount)
                if CheckAction in legal_actions:
                    return CheckAction()
                return FoldAction()
                
        
        elif len(board_cards)==0: #we are small blind
            if hand in pre_flop_fold:
                # if CheckAction in legal_actions:
                #     return CheckAction()
                return FoldAction()
            if opp_pip > 2:
                if hand in great_preflop:
                    if RaiseAction in legal_actions:
                        return RaiseAction(min(max_raise,int(2.5 * opp_pip)))
                else:
                    if continue_cost > equity*pot:
                        return FoldAction()
                    else:
                        return CallAction()
            if RaiseAction in legal_actions:        
                return RaiseAction(min(max_raise,int(2.5 * opp_pip)))
        
        
        #postflop logic
        
        hand_type = eval7.handtype(hand_rank)
        equity = calculate_hand_equity([card for card in my_cards], [card for card in board_cards])
        #if equity > initial_equity:
            #equity = equity*equity_multipliers['improved_equity']
        if len(my_cards) == 3:
            #equity += .3
            equity = equity*equity_multipliers['won_bid']
        # if continue_cost > equity*pot:
        #     return FoldAction
        if equity >= 0.65:
            if RaiseAction in legal_actions:
                if continue_cost >= int(.9*max_raise):
                    return CallAction()
                else:
                    return RaiseAction(int(0.9*max_raise))
        elif equity >= 0.5:
            if RaiseAction in legal_actions:
                if continue_cost >= min(max_raise, int(0.7*(pot))):
                    return FoldAction()

            if RaiseAction in legal_actions:
                return RaiseAction(min(max_raise, int(0.7*(pot))))
        else:
            if CheckAction in legal_actions:
                return CheckAction()
            else:
                return FoldAction()
        
        if CheckAction in legal_actions:
            return CheckAction()
        if CallAction in legal_actions:
            return CallAction()
        return FoldAction()
        


if __name__ == '__main__':
    run_bot(Player(), parse_args())
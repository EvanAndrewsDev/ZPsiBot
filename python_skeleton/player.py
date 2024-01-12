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

pocket_2_max, pocket_2_min = 17563648, 327680

strength_dict = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A':14}

deck = generate_deck()

all_hands_2_str = generate_all_hands(deck,2)
all_hands_2 = [[eval7.Card(hand[:2]) , eval7.Card(hand[2:])] for hand in all_hands_2_str]
all_hands_3_str = generate_all_hands(deck,3)
all_hands_3 = [[eval7.Card(hand[:2]) , eval7.Card(hand[2:])] for hand in all_hands_3_str]

pre_flop_fold = []
for hand in all_hands_2_str:
    if hand[1] != hand[3] and hand[0] != hand[2] and (strength_dict[hand[0]] + strength_dict[hand[2]] < 14):
        pre_flop_fold.append(hand)
pre_flop_fold = [[eval7.Card(hand[:2]) , eval7.Card(hand[2:])] for hand in pre_flop_fold]

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
        big_blind = bool(active)
        if RaiseAction in legal_actions:
           min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
           min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
           max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
           print(min_raise, max_raise, my_stack, opp_stack, my_pip, opp_pip)
        
        # if CheckAction in legal_actions:
        #     return CheckAction()
        # elif BidAction in legal_actions:
        #     return BidAction(int(random.random()*my_stack)) # random bid between 0 and our stack
        # return CallAction()
    
        #___myLogic___
        all_cards = my_cards + board_cards
        hand = [eval7.Card(s) for s in all_cards]
        my_score = eval7.evaluate(hand)

        if BidAction in legal_actions:
            if opp_bid + 1 > my_stack:
                return BidAction(my_stack)
            return opp_bid + 1

        if street == 0:
            great_preflop = [hand for hand in all_hands_2 if ((hand[0] == hand[2] and strength_dict[hand[0]] + strength_dict[hand[2]] >= 18) or strength_dict[hand[0]] + strength_dict[hand[2]] >= 26)]
            if big_blind: #we are small blind
                if hand in pre_flop_fold:
                    if CheckAction in legal_actions:
                        return CheckAction()
                    return FoldAction()
                
                if hand in great_preflop:
                    if RaiseAction in legal_actions:
                        return RaiseAction(min(int(3.2*opp_pip), max_raise))
                    elif CheckAction in legal_actions:
                        return CheckAction()
                    return FoldAction()
                else:
                    if eval7.evaluate(hand) > 0.9 * pocket_2_max:
                        return RaiseAction(max_raise)
                    
                    if hand in pre_flop_fold:
                        if CheckAction in legal_actions:
                            return CheckAction()
                        return FoldAction()
                    elif hand in great_preflop:
                        return RaiseAction(min(int(3.2*opp_pip), max_raise))
                    if CheckAction in legal_actions:
                        return CheckAction()
                    return FoldAction()
                    
            
            else: #we are small blind
                if hand in pre_flop_fold:
                    if CheckAction in legal_actions:
                        return CheckAction()
                    return FoldAction()
                if opp_pip > 2:
                    if hand in great_preflop:
                        return RaiseAction(min(max_raise,int(2.5 * opp_pip)))
                return RaiseAction(min(max_raise,int(2.5 * opp_pip)))



if __name__ == '__main__':
    # hand = ["7s", "2d"]
    # hand = [eval7.Card(s) for s in hand]

    # # Get the hand rank using eval7
    # hand_rank = eval7.evaluate(hand)
    # print("hand rank: ", hand_rank)
    run_bot(Player(), parse_args())
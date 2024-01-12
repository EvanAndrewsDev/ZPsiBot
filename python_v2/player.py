from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction, BidAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import random
import eval7
import math


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
        
        if RaiseAction in legal_actions:
           min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
           min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
           max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
           print(min_raise, max_raise, my_stack, opp_stack, my_pip, opp_pip)

        # strength_dict = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A':14}

        # hand_rating = 0

        # card1 = my_cards[0]
        # card2 = my_cards[1]

        # rank_strength = (strength_dict[card1[0]] + strength_dict[card2[0]])/2
        # hand_rating += rank_strength
        # if card1[0] == card2[0]:
        #     hand_rating += strength_dict[card1[0]]

        # if hand_rating > 12:
        #     if RaiseAction in legal_actions:
        #         return RaiseAction(max_raise)
        #     elif BidAction in legal_actions:
        #         return BidAction(int(my_stack*0.3))
        #     else:
        #         return CheckAction()
        # else:
        #     if CheckAction in legal_actions:
        #         return CheckAction()
        #     elif BidAction in legal_actions:
        #         return BidAction(int(my_stack*0.1))
        #     return FoldAction()
        

        if street == 0:
            willraise = False

            totalcards = my_cards + board_cards
            hand = [eval7.Card(s) for s in totalcards]
            score = math.log2(eval7.evaluate(hand))
            handtype = eval7.handtype(eval7.evaluate(hand))

            card1 = my_cards[0]
            card2 = my_cards[1]

            if card1[1] == card2[1]:
                score += 3

            if handtype == "Pair" and score > 25 + continue_cost/400 or handtype == "High Card" and score > 30+continue_cost/400:
                willraise = True

            if willraise:
                if RaiseAction in legal_actions:
                    # print(continue_cost + 100*(score/24))
                    return RaiseAction(int(continue_cost + 100*(score/24)))

            else:
                if CallAction in legal_actions and score>20:
                    return CallAction()
                if CheckAction in legal_actions:
                    return CheckAction()
                else:
                    return FoldAction()

        else:
            if BidAction in legal_actions:
                return BidAction(int(my_stack*0.5))
            
            else:
                totalcards = my_cards + board_cards
                hand = [eval7.Card(s) for s in totalcards]
                score = math.log2(eval7.evaluate(hand))

                if score > 30:
                    if RaiseAction in legal_actions:
                        return RaiseAction(max_raise)

                elif score < 15 or (continue_cost > 80 and score < 21):
                    if CheckAction in legal_actions:
                        return CheckAction()
                
                    return FoldAction()

                else:
                    if CallAction in legal_actions:
                        return CallAction()
                    elif CheckAction in legal_actions:
                        return CheckAction()
                    else:
                        return FoldAction()

            



        





if __name__ == '__main__':
    run_bot(Player(), parse_args())

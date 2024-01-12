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

        self.BB = big_blind
        card1 = my_cards[0]
        card2 = my_cards[1]

        suited = False
        if card1[1] == card2[1]:
            suited = True

        rankset = {card1[0], card2[0]}

        if not big_blind: #BUTTON OPENING RANGES
            action = CheckAction()
            if not suited:
                folds = [{"Q", "3"}, {"Q", "2"}, 
                        {"J", "4"}, {"J", "3"}, {"J", "2"}, 
                        {"T", "4"}, {"T", "3"}, {"T", "2"}, 
                        {"9", "4"}, {"9", "3"}, {"9", "2"}, 
                        {"8", "4"}, {"8", "3"}, {"8", "2"},
                        {"7", "3"}, {"7", "2"},
                        {"6", "3"}, {"6", "2"},
                        {"5", "2"},
                        {"4", "2"},
                        {"3", "2"},]
                if rankset in folds:
                    action = "fold"
                else:
                    action = "raise"

            self.gtopreflop = action

        else: #BB OPENING RANGES
            if suited:
                bet3 = [{"A", "K"}, {"A", "Q"}, {"A", "J"}, {"A", "T"},{"A", "9"}, {"A", "8"}, 
                        {"K", "Q"}, {"K", "J"}, {"K", "T"},{"K", "9"}, {"K", "8"}, 
                        {"Q", "J"}, {"Q", "T"},{"Q", "9"}, {"Q", "8"}, 
                        {"J", "T"}, {"J", "9"}, 
                        {"T", "9"}, {"T", "8"}, {"T", "7"}, 
                        {"9", "8"}, {"9", "7"}, 
                        {"8", "7"}, 
                        {"7", "6"}, 
                        {"6", "5"}, 
                        {"5", "4"}, ]
                
                call = [{"A", "7"}, {"A", "6"}, {"A", "5"},{"A", "4"}, {"A", "3"}, {"A", "2"},
                        {"K", "7"}, {"K", "6"}, {"K", "5"}, {"K", "4"}, {"K", "3"}, {"K", "2"}, 
                        {"Q", "7"}, {"Q", "6"}, {"Q", "5"}, {"Q", "4"}, {"Q", "3"}, {"Q", "2"}, 
                        {"J", "8"}, {"J", "7"}, {"J", "6"}, {"J", "5"}, {"J", "4"}, {"J", "3"}, {"J", "2"}, 
                        {"T", "6"}, {"T", "5"}, {"T", "4"}, {"T", "3"}, {"T", "2"}, 
                        {"9", "6"}, {"9", "5"}, {"9", "4"}, {"9", "3"}, {"9", "2"}, 
                        {"8", "6"}, {"8", "5"}, {"8", "4"}, {"8", "3"}, {"8", "2"}, 
                        {"7", "5"}, {"7", "4"}, {"7", "3"}, {"7", "2"}, 
                        {"6", "4"}, {"6", "3"}, {"6", "2"}, 
                        {"5", "3"}, ]
                
                if rankset in bet3:
                    action = "3bet"
                elif rankset in call:
                    action = "call"
                else:
                    action = "fold"
                
            else:
                bet3 = [{"A", "A"}, {"A", "K"},{"A", "Q"}, {"A", "J"},
                        {"K", "K"}, {"K", "Q"}, 
                        {"Q", "Q"},
                        {"J", "J"},
                        {"T", "T"},
                        {"9", "9"},
                        {"8", "8"},
                        {"7", "7"}, ]

                call = [{"A", "T"}, {"A", "9"}, {"A", "8"}, {"A", "7"}, {"A", "6"}, {"A", "5"}, {"A", "4"}, {"A", "3"}, {"A", "2"},
                        {"K", "J"}, {"K", "T"}, {"K", "9"}, {"K", "8"}, {"K", "7"}, {"K", "6"}, {"K", "5"}, {"K", "4"}, {"K", "3"}, {"K", "2"}, 
                        {"Q", "J"}, {"Q", "T"}, {"Q", "9"}, {"Q", "8"}, {"Q", "7"}, {"Q", "6"}, {"Q", "5"}, {"Q", "4"}, {"Q", "3"},  
                        {"J", "T"}, {"J", "9"}, {"J", "8"}, {"J", "7"}, {"J", "6"}, {"J", "5"}, 
                        {"T", "9"}, {"T", "8"}, {"T", "7"}, {"T", "6"}, {"T", "5"}, 
                        {"9", "8"}, {"9", "7"}, {"9", "6"}, {"9", "5"}, 
                        {"8", "7"}, {"8", "6"}, {"8", "5"}, 
                        {"7", "6"}, {"7", "5"}, 
                        {"6", "5"}, 
                        {"5", "4"}, ]
                
                if rankset in bet3:
                    action = "3bet"
                elif rankset in call:
                    action = "call"
                else:
                    action = "fold"

            self.gtopreflop = action

        if not big_blind: #BUTTON FACES 3BET RANGES
            bet4 = [{'A', 'A'}, {'K', 'K'}, {'Q', 'Q'}, {'J', 'J'}, {'T', 'T'}, {'A', 'K'}]
            if not suited:
                folds = [{"K", "7"}, {"K", "6"}, {"K", "5"}, {"K", "4"}, {"K", "3"}, {"K", "2"}, 
                         {"Q", "7"}, {"Q", "6"}, {"Q", "5"}, {"Q", "4"}, {"Q", "3"}, {"Q", "2"}, 
                         {"J", "7"}, {"J", "6"}, {"J", "5"}, {"J", "4"}, {"J", "3"}, {"J", "2"}, 
                         {"T", "7"}, {"T", "6"}, {"T", "5"}, {"T", "4"}, {"T", "3"}, {"T", "2"}, 
                         {"9", "7"}, {"9", "6"}, {"9", "5"}, {"9", "4"}, {"9", "3"}, {"9", "2"},
                         {"8", "6"}, {"8", "5"}, {"8", "4"}, {"8", "3"}, {"8", "2"}, 
                         {"7", "6"}, {"7", "5"}, {"7", "4"}, {"7", "3"}, {"7", "2"}, 
                         {"6", "5"}, {"6", "4"}, {"6", "3"}, {"6", "2"}, 
                         {"5", "4"}, {"5", "3"}, {"5", "2"}, 
                         {"4", "3"}, {"4", "2"}, 
                         {"3", "2"}, ]
                
                if rankset in bet4:
                    btnface3bet = "raise"
                elif rankset in folds:
                    btnface3bet = "fold"
                else:
                    btnface3bet = "call"

            else:
                folds = [{"T", "3"}, {"9", "3"}, {"8", "3"}, {"J", "2"}, {"T", "2"}, {"9", "2"}, {"8", "2"}, {"7", "2"}]
                if rankset in bet4:
                    btnface3bet = "raise"
                elif rankset in folds:
                    btnface3bet = "fold"
                else:
                    btnface3bet = "call"

            self.btnface3bet = btnface3bet

        else: #BB FACES 4BET RANGES
            bet5 = [{'A', 'A'}, {'K', 'K'}, {'Q', 'Q'}, {'J', 'J'}, {'T', 'T'}]
            if not suited:
                call = [{"A", "Q"}, {"K", "Q"}, {"A", "J"}, {"9", "9"}, {"8", "8"}, {"7", "7"}, {"6", "6"}, {"5", "5"}, ]

                if rankset in bet5:
                    BBface4bet = "raise"
                elif rankset in call:
                    BBface4bet = "call"
                else:
                    BBface4bet = "fold"

            else:
                call = [{"A", "Q"}, {"A", "J"}, {"A", "T"},{"A", "9"}, {"A", "5"}, {"A", "4"}, {"A", "3"}, {"A", "2"}, 
                        {"K", "Q"}, {"K", "J"}, {"K", "T"}, {"K", "9"}, {"K", "8"}, {"K", "7"}, 
                        {"Q", "J"}, {"Q", "T"}, {"Q", "9"}, {"Q", "8"}, 
                        {"J", "T"}, {"J", "9"}, {"J", "8"}, 
                        {"T", "9"}, {"T", "8"}, 
                        {"9", "8"}, {"9", "7"}, 
                        {"8", "7"}, 
                        {"7", "6"}, 
                        {"6", "5"}, 
                        {"5", "4"}, ]
                
                if rankset in bet5:
                    BBface4bet = "raise"
                elif rankset in call:
                    BBface4bet = "call"
                else:
                    BBface4bet = "fold"

            self.BBface4bet = BBface4bet

    def calculate_draw_strength(self, my_cards, community_cards):
        pass

    def calculate_hand_strength(self, my_cards, community_cards, opp_num, iters):
        """
        Estimate Hand Strength: Percentage of Times we win a Hand

        Assumes random cards for opponents
        """
        deck = eval7.Deck()
        my_cards = [eval7.Card(card) for card in my_cards]
        community_cards = [eval7.Card(card) for card in community_cards]

        for card in my_cards:
            deck.cards.remove(card)

        for card in community_cards:
            deck.cards.remove(card)

        wins = 0

        for _ in range(iters):
            deck.shuffle()

            opp_cards = deck.peek(opp_num)

            our_hand = my_cards + community_cards
            opp_hand = opp_cards + community_cards

            our_hand_val = eval7.evaluate(our_hand)
            opp_hand_val = eval7.evaluate(opp_hand)

            if our_hand_val > opp_hand_val:
                wins += 2

            elif our_hand_val == opp_hand_val:
                wins += 1

        return wins/(2*iters)
    
    def clamp(self, low, high, val):
        val1 = min(high, val)
        val1 = max(low, val1)

        return val1

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
        
        if RaiseAction in legal_actions:
           min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
           min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
           max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
           print(min_raise, max_raise, my_stack, opp_stack, my_pip, opp_pip)

        if BidAction in legal_actions: # will update with taking into consideration: blocking (already strong hand), drawing (chance to make big hand)
            return BidAction(int(3*pot))
            
        bb = self.BB

        if street == 0:
            suggest = self.gtopreflop

            if not bb: # You are Button
                if suggest == "fold":
                    return FoldAction()
                elif pot == 3: # first action
                    return RaiseAction(5)
                else: # facing a raise
                    if self.btnface3bet == "raise":
                        return RaiseAction(self.clamp(min_raise, max_raise, 2.2*continue_cost))

                    elif self.btnface3bet == "call":
                        return CallAction()
                    else:
                        return FoldAction()

            else: # You are BB
                if CheckAction in legal_actions: # Button Calls
                    if suggest == "call" or suggest == "fold":
                        return CheckAction()
                    else:
                        return RaiseAction(5)
                    
                elif my_contribution == 2: # Button Raises
                    if suggest == "raise":
                        return RaiseAction(self.clamp(min_raise, max_raise, 4*continue_cost))
                    elif suggest == "call":
                        return CallAction()
                    else:
                        return FoldAction()

                elif my_contribution > 2: # Button ReRaises
                    if self.BBface4bet == "raise":
                        return RaiseAction(max_raise)
                    elif self.BBface4bet == "call":
                        return CallAction()
                    else:
                        return FoldAction()

        else:
            if opp_bid >= my_bid:
                opp_num = 3
            else:
                opp_num = 2

            strength = self.calculate_hand_strength(my_cards, board_cards, opp_num, 100)

            raise_amount = int(my_pip + 2*continue_cost + 0.5*pot)
            raise_cost = int(2*continue_cost + 0.5*pot)


        if RaiseAction in legal_actions and raise_cost < my_stack:
            commit_action = RaiseAction(raise_amount)
        elif CallAction in legal_actions and continue_cost <= my_stack:
            commit_action = CallAction()
        else:
            commit_action = FoldAction()


        if continue_cost > 0:
            pot_odds = continue_cost/(continue_cost + pot)
            intimidation = 0
            if continue_cost/pot > 0.33:
                intimidation = -0.33
            strength += intimidation

            if strength >= pot_odds:
                if random.random() < strength and strength > 0.6:
                    my_action = commit_action
                else:
                    my_action = CallAction()

            if strength < pot_odds:
                if strength < 0.1 and random.random()<0.05:
                    if RaiseAction in legal_actions:
                        my_action = commit_action
                else:
                    my_action = FoldAction()

        else:
            if strength > 0.6 and random.random() < strength:
                my_action = commit_action
            else:
                my_action = CheckAction()

        return my_action

if __name__ == '__main__':
    run_bot(Player(), parse_args())

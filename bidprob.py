import eval7
import random
from itertools import combinations
import pickle

def generate_random_flop(starting_hand):
    deck = eval7.Deck()
    available = [card for card in deck.cards if card not in starting_hand]
    flop_cards = random.sample(available, 3)
    return flop_cards

def generate_all_hands():
    deck = eval7.Deck()
    starting_hands = list(combinations(deck,2))
    result = [list(hand) for hand in starting_hands]
    return result

def generate_all_flops():
    deck = eval7.Deck()
    flops = list(combinations(deck.cards,3))
    list_flops = [list(flop) for flop in flops]
    return list_flops

def simulate_rest_game(hand, flop):
    NUM_REPS = 20
    print("hand:", hand)
    print("flop:", flop)
    deck = eval7.Deck()
    available = [card for card in deck.cards if card not in hand and card not in flop]
    wins_with_bonus = 0
    wins_without_bonus = 0
    for _ in range(NUM_REPS):
        opponent = random.choice(playable)
        new_available = [card for card in available if card not in opponent]
        bonus_card = [new_available.pop(0)]
        turn_and_river = random.sample(new_available,2)
        our_total = hand + flop + turn_and_river
        opponent_total = opponent + flop + turn_and_river
        if eval7.evaluate(our_total + bonus_card) > eval7.evaluate(opponent_total):
            wins_with_bonus += 1
        if eval7.evaluate(our_total) > eval7.evaluate(opponent_total + bonus_card):
            wins_without_bonus += 1
    return wins_with_bonus/NUM_REPS, wins_without_bonus/NUM_REPS



if __name__ == "__main__":

    bad1 = [(1,2), (1,3), (1,4), (5,1), (6,1), (6,2), (7,1), (7,2), (8,1), (8,2), (8,3), (9,1)]
    bad = bad1.copy()
    for combo in bad1:
        bad.append((combo[1], combo[0]))
        bad.append(combo)

    hands = generate_all_hands()
    flops = generate_all_flops()
    playable = [hand for hand in hands if hand[0].suit == hand[1].suit or (hand[0].rank, hand[1].rank) not in bad]

    postflop_to_winprobs = {}
    total = 0
    for hand in playable:
        print(hand)
        if total >= 100:
            break
        for flop in flops:
            probs = simulate_rest_game(hand,flop)
            postflop_to_winprobs[(tuple(hand),tuple(flop))] = probs
            total += 1
    
    with open('probs.pkl', 'wb') as pickle_file:
        pickle.dump(postflop_to_winprobs, pickle_file)
    

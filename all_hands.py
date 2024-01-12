from itertools import combinations

def generate_deck():
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    suits = ['h', 'd', 'c', 's']
    deck = [rank + suit for rank in ranks for suit in suits]
    return deck

def generate_all_hands(deck):
    combos = list(combinations(deck, 3))
    return [c[0] + c[1] + c[2] for c in combos]

# Example usage
deck = generate_deck()
all_hands = generate_all_hands(deck)

print(all_hands)
print("Number : ", len(all_hands))
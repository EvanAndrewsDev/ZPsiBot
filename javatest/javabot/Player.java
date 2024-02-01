// Importing required modules
const { FoldAction, CallAction, CheckAction, RaiseAction, BidAction } = require('skeleton/actions');
const { GameState, TerminalState, RoundState } = require('skeleton/states');
const { NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND } = require('skeleton/states');
const { Bot } = require('skeleton/bot');
const { parse_args, run_bot } = require('skeleton/runner');
const random = require('random');
const eval7 = require('eval7');
const math = require('math');
const combinations = require('combinations');

function generate_deck() {
    const ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'];
    const suits = ['h', 'd', 'c', 's'];
    const deck = ranks.flatMap(rank => suits.map(suit => rank + suit));
    return deck;
}

function generate_all_hands(deck, number) {
    const combos = combinations(deck, number);
    return combos.map(combo => combo.join(''));
}

function calculate_hand_equity(hand, board) {
    const deck = generate_deck();
    const remaining_deck = deck.filter(card => !hand.includes(card) && !board.includes(card));
    let wins = 0;
    const iterations = 100;
    for (let i = 0; i < iterations; i++) {
        random.shuffle(remaining_deck);
        const opponent_hand = remaining_deck.slice(0, 2);
        const future_board = board.concat(remaining_deck.slice(2, 7 - board.length));
        const my_score = eval7.evaluate(hand.concat(future_board).map(card => new eval7.Card(card)));
        const opponent_score = eval7.evaluate(opponent_hand.concat(future_board).map(card => new eval7.Card(card)));
        if (my_score > opponent_score) {
            wins += 1;
        }
    }
    return wins / iterations;
}

const equity_multipliers = {
    'consistent_hand': 1.5,
    'likely_loss': .25,
    'won_bid': 1.3,
    'improved_equity': 1.3
};

const hand_to_equity = {
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
};

const equity_multipliers = {
    'consistent_hand': 1.5,
    'likely_loss': .25,
    'won_bid': 1.3,
    'improved_equity': 1.3
};

const pocket_2_max = 17563648;
const pocket_2_min = 327680;
const deck = generate_deck();
const all_hands_2_str = generate_all_hands(deck, 2);
const all_hands_2 = all_hands_2_str.map(hand => [new eval7.Card(hand.slice(0, 2)), new eval7.Card(hand.slice(2))]);
const all_hands_3_str = generate_all_hands(deck, 3);
const all_hands_3 = all_hands_3_str.map(hand => [new eval7.Card(hand.slice(0, 2)), new eval7.Card(hand.slice(2))]);
const pre_flop_fold = all_hands_2.filter(hand => hand[0].suit !== hand[1].suit && hand[0].rank !== hand[1].rank && (hand[0].rank + hand[1].rank < 10));

const great_preflop = all_hands_2.filter(h => (h[0].rank === h[1].rank && h[0].rank + h[1].rank >= 14) || h[0].rank + h[1].rank >= 22);

class Player extends Bot {
    constructor() {
        super();
    }

    handle_new_round(game_state, round_state, active) {
        const my_bankroll = game_state.bankroll;
        const game_clock = game_state.game_clock;
        const round_num = game_state.round_num;
        const my_cards = round_state.hands[active];
        const big_blind = Boolean(active);
    }

    handle_round_over(game_state, terminal_state, active) {
        const my_delta = terminal_state.deltas[active];
        const previous_state = terminal_state.previous_state;
        const street = previous_state.street;
        const my_cards = previous_state.hands[active];
        const opp_cards = previous_state.hands[1 - active];
    }

    get_action(game_state, round_state, active) {
        const legal_actions = round_state.legal_actions();
        const street = round_state.street;
        const my_cards = round_state.hands[active];
        const board_cards = round_state.deck.slice(0, street);
        const my_pip = round_state.pips[active];
        const opp_pip = round_state.pips[1 - active];
        const my_stack = round_state.stacks[active];
        const opp_stack = round_state.stacks[1 - active];
        const my_bid = round_state.bids[active];
        const opp_bid = round_state.bids[1 - active];
        const continue_cost = opp_pip - my_pip;
        const my_contribution = STARTING_STACK - my_stack;
        const opp_contribution = STARTING_STACK - opp_stack;
        const pot = my_contribution + opp_contribution;
        const big_blind = Boolean(active);

        if (RaiseAction in legal_actions) {
            const [min_raise, max_raise] = round_state.raise_bounds();
            const min_cost = min_raise - my_pip;
            const max_cost = max_raise - my_pip;
        }

        function bail_option(legal_actions) {
            if (CheckAction in legal_actions) {
                return new CheckAction();
            }
            return new FoldAction();
        }

        const all_cards = my_cards.concat(board_cards);
        const hand = all_cards.map(card => new eval7.Card(card));
        const hand_rank = eval7.evaluate(hand);
        const hand_type = eval7.handtype(hand_rank);

        const equity = calculate_hand_equity(my_cards, board_cards);

        if (BidAction in legal_actions) {
            const boldness = 1;

            if (my_cards[0][0] === my_cards[1][0]) {
                const ranks = [];
                for (const c of board_cards) {
                    if (!ranks.includes(c[0])) {
                        ranks.push(c[0]);
                    }
                }
                if (ranks.length <= 2) {
                    const bidamount = Math.min(Math.floor(my_stack * .75), Math.floor(.75 * pot));
                    return new BidAction(bidamount);
                } else {
                    return new BidAction(Math.floor(.2 * my_stack * boldness));
                }
            } else if (my_cards[0][1] === my_cards[1][1]) {
                const suits = [];
                let preferred;
                for (const c of board_cards) {
                    if (suits.includes(c[1])) {
                        preferred = c[1];
                    }
                    if (!suits.includes(c[1])) {
                        suits.push(c[1]);
                    }
                }
                if (suits.length <= 2 && preferred === my_cards[0][1]) {
                    return new BidAction(Math.floor(.3 * my_stack * boldness));
                }
            }
            return new BidAction(my_stack / 2);
        }

        const initial_equity = equity;

        if (!big_blind && board_cards.length === 0) {
            if (great_preflop.includes(hand)) {
                if (RaiseAction in legal_actions) {
                    return new RaiseAction(Math.min(4 * opp_pip, max_raise));
                }
            } else if (pre_flop_fold.includes(hand)) {
                return new FoldAction();
            } else {
                if (CheckAction in legal_actions) {
                    return new CheckAction();
                }
            }
            if (pre_flop_fold.includes(hand)) {
                console.log('hand should be folded');
                if (CheckAction in legal_actions) {
                    return new CheckAction();
                }
                return new FoldAction();
            } else {
                if (eval7.evaluate(hand) > 0.9 * pocket_2_max) {
                    if (RaiseAction in legal_actions) {
                        return new RaiseAction(max_raise);
                    }
                }
                if (pre_flop_fold.includes(hand)) {
                    if (CheckAction in legal_actions) {
                        return new CheckAction();
                    }
                    return new FoldAction();
                } else if (great_preflop.includes(hand) && RaiseAction in legal_actions) {
                    const raiseamount = Math.min(max_raise - 1, 3.2 * opp_pip);
                    return new RaiseAction(raiseamount);
                }
                if (CheckAction in legal_actions) {
                    return new CheckAction();
                }
                return new FoldAction();
            }
        } else if (board_cards.length === 0) {
            if (pre_flop_fold.includes(hand)) {
                return new FoldAction();
            }
            if (opp_pip > 2) {
                if (great_preflop.includes(hand)) {
                    if (RaiseAction in legal_actions) {
                        return new RaiseAction(Math.min(max_raise, 2.5 * opp_pip));
                    }
                } else {
                    if (continue_cost > equity * pot) {
                        return new FoldAction();
                    } else {
                        return new CallAction();
                    }
                }
            }
            if (RaiseAction in legal_actions) {
                return new RaiseAction(Math.min(max_raise, 2.5 * opp_pip));
            }
        }

        const hand_type = eval7.handtype(hand_rank);
        const equity = calculate_hand_equity(my_cards, board_cards);

        if (my_cards.length === 3) {
            equity = equity * equity_multipliers['won_bid'];
        }

        if (equity >= 0.65) {
            if (RaiseAction in legal_actions) {
                if (continue_cost >= 0.9 * max_raise) {
                    return new CallAction();
                } else {
                    return new RaiseAction(0.9 * max_raise);
                }
            }
        } else if (equity >= 0.5) {
            if (RaiseAction in legal_actions) {
                if (continue_cost >= Math.min(max_raise, 0.7 * pot)) {
                    return new FoldAction();
                }
            }
            if (RaiseAction in legal_actions) {
                return new RaiseAction(Math.min(max_raise, 0.7 * pot));
            }
        } else {
            if (CheckAction in legal_actions) {
                return new CheckAction();
            } else {
                return new FoldAction();
            }
        }
        if (CheckAction in legal_actions) {
            return new CheckAction();
        }
        if (CallAction in legal_actions) {
            return new CallAction();
        }
        return new FoldAction();
    }
}

if (require.main === module) {
    run_bot(new Player(), parse_args());
}



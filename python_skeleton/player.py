'''
Simple example pokerbot, written in Python.
'''
import eval7
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import random


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

        opponent_bounty = []
        
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
        my_bounty = round_state.bounties[active]  # your current bounty rank

        if round_num % 25 == 1:
            self.opponent_bounty = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]

        print(f"round {round_num}")
        print(f"possible opponent bounty: {self.opponent_bounty}")
        pass

    def convert_to_rank(hand):
        rank = []
        for x in hand:
            rank.append(int(x[:1]))
        return rank

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
        board_cards = previous_state.deck[:street]  # the board cards
        my_pip = previous_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = previous_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        
        my_bounty_hit = terminal_state.bounty_hits[active]  # True if you hit bounty
        opponent_bounty_hit = terminal_state.bounty_hits[1-active] # True if opponent hit bounty
        bounty_rank = previous_state.bounties[active]  # your bounty rank

        # The following is a demonstration of accessing illegal information (will not work)
        opponent_bounty_rank = previous_state.bounties[1-active]  # attempting to grab opponent's bounty rank

        if my_bounty_hit:
            print("I hit my bounty of " + bounty_rank + "!")
        if opponent_bounty_hit:
            print("Opponent hit their bounty of " + opponent_bounty_rank + "!")
            community_cards = board_cards
            if len(opp_cards) != 0:
                community_cards += opp_cards
                community_cards = [card[0] for card in community_cards]
                # print(f"community cards: {community_cards}")
                # print(f"opponent bounty: {self.opponent_bounty}")
                for x in self.opponent_bounty:
                    if x not in community_cards:
                        self.opponent_bounty.remove(x)
        elif my_delta < 0:
            community_cards = board_cards
            if len(opp_cards) != 0:
                community_cards += opp_cards
            community_cards = [card[0] for card in community_cards]
            for x in self.opponent_bounty:
                if x in community_cards:
                    self.opponent_bounty.remove(x)


    def calculate_strength(self, my_cards, board_cards):
        print(f"my cards: {my_cards}")
        print(f"board card: {board_cards}")
        MC_ITER = 100
        my_cards = [eval7.Card(card) for card in my_cards]
        board_cards = [eval7.Card(card) for card in board_cards]
        deck = eval7.Deck()
        for card in my_cards + board_cards:
            deck.cards.remove(card)
        
        score = 0
        for _ in range(MC_ITER):
            deck.shuffle()
            draw_number = 2 + (5 - len(board_cards))
            draw = deck.peek(draw_number)
            opp_draw = draw[:2]
            board_draw = draw[2:]
            my_hand = my_cards + board_cards + board_draw
            opp_hand = opp_draw + board_cards + board_draw
            my_value = eval7.evaluate(my_hand)
            opp_value = eval7.evaluate(opp_hand)
            if my_value > opp_value:
                score += 1
            elif my_value < opp_value:
                score += 0
            else:
                score += 0.5
        
        win_rate = score / MC_ITER
        print(f"win rate: {win_rate}")
        return win_rate

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
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_bounty = round_state.bounties[active]  # your current bounty rank
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot

        if len(self.opponent_bounty) == 1 and (self.opponent_bounty[0] in [card[0] for card in my_cards] or self.opponent_bounty[0] in [card[0] for card in board_cards]):
            continue_cost *= 1.5
            my_pip *= 1.5
        
        if RaiseAction in legal_actions:
           min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
           min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
           max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        win_rate = self.calculate_strength(my_cards, board_cards)
        pot_odds = continue_cost / (my_pip + opp_pip + continue_cost + 0.1) # min probability of winning a hand to justify calling
        rounds_left = 1
        if street == 0:
            rounds_left = 4
        if street == 3:
            rounds_left = 3
        if street == 4:
            rounds_left = 2
        if street == 5:
            rounds_left = 1
        if my_bounty in [card[0] for card in my_cards] or my_bounty in [card[0] for card in board_cards]:
            pot_odds = continue_cost / (my_pip + opp_pip * 1.5 + continue_cost + 0.1)
        print(f"pot odd: {pot_odds}")
        if continue_cost > 0 and win_rate < 0.5:
            print("folded for continuation cost")
            return FoldAction()
        if continue_cost > 50 and win_rate < 0.65:
            print("folded for 50")
            return FoldAction()
        if continue_cost > 100 and win_rate < 0.75:
            print("folded for 100")
            return FoldAction()
        if continue_cost > 200 and win_rate < 0.85:
            print("folded for 200")
            return FoldAction()
        if RaiseAction in legal_actions:
            if continue_cost == 0 and street == 0 and (my_bounty in [card[0] for card in my_cards] or my_bounty in [card[0] for card in board_cards]):
                print(f"bounty hit: {my_bounty} in {my_cards} or {board_cards}")
                print(f"raised by min: {min_raise}")
                return RaiseAction(min_raise)
            if continue_cost == 0 and street == 3 and (my_pip + opp_pip) < 50 and (my_bounty in [card[0] for card in my_cards] or my_bounty in [card[0] for card in board_cards]):
                print(f"bounty hit: {my_bounty} in {my_cards} or {board_cards}")
                print(f"raised by min: {min_raise}")
                return RaiseAction(min_raise)
            if win_rate > 0.95 and win_rate > pot_odds:
                print(f"raised by max: {int(max_raise/rounds_left**2)}")
                return RaiseAction(int(max_raise/rounds_left**2))
            if win_rate > 0.75 and win_rate > pot_odds:
                print(f"raised by: {max(min_raise, int((max_raise-min_raise) * (win_rate - 0.7)))}")
                return RaiseAction(max(min_raise, int((max_raise-min_raise) * (win_rate - 0.7))))
        if CheckAction in legal_actions:  # check-call
            print("checked")
            return CheckAction()
        if win_rate < 0.4:
            print("folded bc win rate")
            return FoldAction()
        if win_rate < .25 * pot_odds:
            print("folded bc of pot odd")
            return FoldAction()
        print("called")
        return CallAction()


if __name__ == '__main__':
    run_bot(Player(), parse_args())

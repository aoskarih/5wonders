import numpy as np


class Card:
    # savi 0, malmi 1, kivi 2, puu 3, lasi 4, kangas 5, papy 6,
    # Raha 7, armeija 8, pisteitä 9, ratas 10, harppi 11, taulu 12,
    output = [0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0]

    switch_output = [0, 0, 0, 0, 0, 0, 0, 0]

    owner = 10

    def __init__(self, number, name, cost, action, output, amount, color):
        self.cost = cost
        self.name = name
        self.number = number
        self.out_type = output
        self.amount = amount
        self.action = action
        self.color = color          # brown 0, grey 1, yellow 2, blue 3, red 4, green 5, purple 6, wonder 7

    def do_action(self, new_owner):
        self.output = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.switch_output = [0, 0, 0, 0, 0, 0, 0, 0]
        self.owner = new_owner
        if self.action == "simple":
            self.add_to_output(self.out_type, self.amount)
        elif self.action == "mult_simple":
            for i in range(len(self.out_type)):
                self.add_to_output(self.out_type[i], self.amount[i])
        elif self.action == "switch":
            self.switch_output(self.out_type, self.amount)
        elif self.action == "special":
            if self.name == "bazar":
                self.stuff_for_cards(self.out_type, self.amount, 3, 1)
            elif self.name == "vineyard":
                self.stuff_for_cards(self.out_type, self.amount, 3, 0)
            elif self.name == "c_of_commerce":
                for o in self.out_type:
                    self.stuff_for_cards(o, self.amount, 1, 1)
            elif self.name == "arena":
                self.stuff_for_cards(7, 3, 1, 7)
                self.stuff_for_cards(9, 1, 1, 7)
            elif self.name == "lighthouse":
                for o in self.out_type:
                    self.stuff_for_cards(o, self.amount, 1, 2)
            elif self.name == "haven":
                for o in self.out_type:
                    self.stuff_for_cards(o, self.amount, 1, 0)
            elif self.name == "philosophers":
                self.stuff_for_cards(self.out_type, self.amount, 2, 5)
            elif self.name == "traders":
                self.stuff_for_cards(self.out_type, self.amount, 2, 2)
            elif self.name == "workers":
                self.stuff_for_cards(self.out_type, self.amount, 2, 0)
            elif self.name == "craftsmens":
                self.stuff_for_cards(self.out_type, self.amount, 2, 1)
            elif self.name == "magistrates":
                self.stuff_for_cards(self.out_type, self.amount, 2, 3)
            elif self.name == "spies":
                self.stuff_for_cards(self.out_type, self.amount, 2, 4)
            elif self.name == "builders":
                self.stuff_for_cards(self.out_type, self.amount, 3, 7)
            elif self.name == "strategists":
                self.strategists_guild()
            elif self.name == "shipowners":
                self.stuff_for_cards(self.out_type, self.amount, 1, 0)
                self.stuff_for_cards(self.out_type, self.amount, 1, 1)
                self.stuff_for_cards(self.out_type, self.amount, 1, 6)
        elif self.action == "pass": pass

    def add_to_output(self, output, amount):
        self.output[output] = amount

    def switch_resource(self, outputs, amount):
        for o in outputs:
            self.switch_output[o] = amount

    def stuff_for_cards(self, output, amount, peoples, color):
        number = 0
        pl = 0
        if peoples == 3:
            for p in range(3):
                pl = (self.owner + 1 - p) % 6
                index = 0
                for c in game.players[p].cards:
                    if c == 1:
                        if game.cards[index].color == color:
                            number += 1
                    index += 1
            self.output[output] += amount*number
        elif peoples == 2:
            for p in range(3):
                if p == 1:
                    continue
                pl = (self.owner + 1 - p) % 6
                index = 0
                for c in game.players[p].cards:
                    if c == 1:
                        if game.cards[index].color == color:
                            number += 1
                    index += 1
            self.output[output] += amount*number
        elif peoples == 1:
            index = 0
            for c in game.players[self.owner].cards:
                if c == 1:
                    if game.cards[index].color == color:
                        number += 1
                index += 1
            self.output[output] += amount * number

    def strategists_guild(self):
        number = 0
        pl = 0
        for p in range(3):
            if p == 1:
                continue
            pl = (self.owner + 1 - p) % 6
            index = 0
            number += game.players[pl].army_minuses
        self.output[9] += number


class Player:

    def __init__(self, place, wonder):
        self.place = place
        self.cards = np.zeros(138)  # 21 cards per player + 30 phases of wonders
        self.wonder = wonder
        self.money = 3
        self.armies = 0
        self.army_points = 0
        self.army_minuses = 0
        self.minuses = 0
        self.res_vectors = []

    def add_card(self, card):
        self.cards[card] = 1

    def choose_card(self, input):

        # hidden_1 = input and stuff
        # hidden_2 = hidden_1 and stuff
        # .
        # .
        # .
        output = [] # hidden_n and stuff

        return output.index(max(output))

    def switch_resources(self):
        switch_cards = []
        for i in range(len(self.cards)):
            if self.cards[i] and game.cards[i].action == "switch":
                switch_cards.append(game.cards[i])

        outputs = np.zeros((len(switch_cards), 8))
        for i in range(len(switch_cards)):
            switch_cards[i].do_action(self.place)
            outputs[i] = switch_cards[i].switch_output

        outputs = [np.nonzero(o)[0] for o in outputs]
        self.resource_vectors(outputs)


    def resource_vectors(self, outputs, level=0, places=[]):
        for i in range(len(outputs[level])):
            if level == len(outputs) - 1:
                vector = [0, 0, 0, 0, 0, 0, 0, 0]
                for j in places:
                    vector[j] += 1
                self.res_vectors.append(vector)
            else:
                places.append(i)
                self.resource_vectors(outputs, level=level+1, places=places)

    def all_resources(self):
        res = [0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(len(self.cards)):
            if self.cards[i] and game.cards[i].action == "switch":
                game.cards[i].do_action(self.place)
                res += game.cards[i].switch_output
        res += self.own_resources()
        return res


    def own_resources(self):
        res = np.zeros((8, 1))

        if "alex" in self.wonder:
            res[4] += 1
        elif "baby" in self.wonder:
            res[0] += 1
        elif "ephe" in self.wonder:
            res[6] += 1
        elif "giza" in self.wonder:
            res[2] += 1
        elif "rhod" in self.wonder:
            res[1] += 1

        for card in self.cards[:7]:
            card.do_action(self.place)
            res += card.output[:6]
        for card in self.cards[12:14]:
            card.do_action(self.place)
            res += card.output[:6]
        for card in self.cards[35:48]:
            card.do_action(self.place)
            res += card.output[:6]
        res[7] = self.money
        return res


class Game:

    players = []
    cards = []

    def __init__(self):
        self.load_cards()

    def game_cycle(self):

        for era in range(3):
            self.era(era+1)



    def load_cards(self):
        file = open("cards", 'r')
        lines = file.readlines()
        for line in lines:
            l = line.split()
            if l[0] == "Number":
                continue
            if l[3] == "switch" or l[3] == "special" or l[3] == "mult_simple":
                cost = list(l[2])
                output = list(l[4])
                if l[3] == "mult_simple":
                    amount = list(l[5])
                    self.cards.append(Card(int(l[0]), l[1], [int(i) for i in cost], l[3], [int(i) for i in output], [int(i) for i in amount], l[6]))
                else:
                    self.cards.append(Card(int(l[0]), l[1], [int(i) for i in cost], l[3], [int(i) for i in output], l[5], l[6]))
            else:
                cost = list(l[2])
                self.cards.append(Card(int(l[0]), l[1], [int(i) for i in cost], l[3], l[4], l[5], l[6]))
        print(len(self.cards))

    def era(self, era):
        cards_for_era = self.cards_for_era(era)
        turn = 0
        while turn < 5:
            used_cards = []
            for p in self.players:
                cards_in_hand = cards_for_era[p.place+turn]
                available = self.input(p.place, cards_in_hand, p.wonder)
                card_weights = p.choose_card(available)
                card_to_be_played = card_weights.index(max(card_weights))
                if available[card_to_be_played] and card_to_be_played != 138:
                    self.cards[card_to_be_played].do_action()
                    if self.cards[card_to_be_played].output[7]:
                        p.money += self.cards[card_to_be_played].output[7]
                    elif self.cards[card_to_be_played].output[8]:
                        p.money += self.cards[card_to_be_played].output[8]
                    p.add_card(card_to_be_played)
                    if card_to_be_played < 108:
                        cards_for_era[p.place+turn].remove(card_to_be_played)
                    else:
                        cards_for_era[p.place + turn].remove(cards_in_hand[0])
                    cost = self.payment(card_to_be_played, p)
                    p.money -= sum(cost)
                    self.players[(p.place - 1) % 6].money += cost[0]
                    self.players[(p.place + 1) % 6].money += cost[1]
                    if self.cards[card_to_be_played].cost[7] != 0:
                        p.money -= self.cards[card_to_be_played].cost[7]
                elif card_to_be_played == 138:
                    card = cards_in_hand[0]
                    cards_for_era[p.place + turn].remove(card)
                    p.money += 3
                else:
                    card = cards_in_hand[0]
                    cards_for_era[p.place + turn].remove(card)
                    p.money += 3
                    p.minuses += 1

        for p in self.players:

            if self.players[(p.place - 1) % 6].


    def input(self, place, cards_in_hand, wonder):

        input = np.zeros((139+4*138, 1))
        input[138] = 1

        for card in cards_in_hand:
            cost = self.payment(card, self.players[place])
            if cost == "no can do":
                input[card] = 0
            elif sum(cost) > self.players[place].money:
                input[card] = 0
            else:
                input[card] = 1


        return

    def payment(self, card, player):
        cost = self.cards[card].cost
        cost = cost-player.own_resources()
        cost = cost.clip(min=0)

        if cost[7] != 0:
            return "no can do"
        if np.all(cost == 0):
            return [0, 0]

        finals = []

        for vec in player.res_vectors:
            cost_vec = cost-vec
            cost_vec = cost_vec.clip(min=0)
            if np.all(cost_vec == 0):
                return [0, 0]
            else:
                final = [0, 0]
                cost_b = cost_vec[:3]
                cost_g = cost_vec[4:6]
                if np.all(cost_b == 0):
                    for i in range(len(cost_b)):
                        if cost_b[i]:
                            if player.cards[26]:
                                if self.players[(player.place - 1) % 6].all_resources()[i]:
                                    a = cost_b[i]
                                    b = self.players[(player.place - 1) % 6].all_resources()[i]
                                    if a <= b:
                                        final[0] += a
                                        cost_b[i] -= a
                                    elif b < a:
                                        final[0] += a-b
                                        cost_b[i] -= a-b
                        if cost_b[i]:
                            if player.cards[27]:
                                if self.players[(player.place + 1) % 6].all_resources()[i]:
                                    a = cost_b[i]
                                    b = self.players[(player.place + 1) % 6].all_resources()[i]
                                    if a <= b:
                                        final[1] += a
                                        cost_b[i] -= a
                                    elif b < a:
                                        final[1] += a - b
                                        cost_b[i] -= a - b
                        if cost_b[i]:
                            if self.players[(player.place - 1) % 6].all_resources()[i]:
                                a = cost_b[i]
                                b = self.players[(player.place - 1) % 6].all_resources()[i]
                                if a <= b:
                                    final[0] += 2*a
                                    cost_b[i] -= a
                                elif b < a:
                                    final[0] += 2*(a - b)
                                    cost_b[i] -= a - b
                        if cost_b[i]:
                            if self.players[(player.place + 1) % 6].all_resources()[i]:
                                a = cost_b[i]
                                b = self.players[(player.place + 1) % 6].all_resources()[i]
                                if a <= b:
                                    final[1] += 2*a
                                    cost_b[i] -= a
                                elif b < a:
                                    final[1] += 2*(a - b)
                                    cost_b[i] -= a - b
                        if cost_b[i]:
                            return "no can do"

                if np.all(cost_g == 0):
                    for i in range(len(cost_g)):
                        if cost_g[i]:
                            if player.cards[28] or player.cards[29]:
                                if self.players[(player.place - 1) % 6].all_resources()[4+i]:
                                    a = cost_g[i]
                                    b = self.players[(player.place - 1) % 6].all_resources()[4+i]
                                    if a <= b:
                                        final[0] += a
                                        cost_g[i] -= a
                                    elif b < a:
                                        final[0] += a-b
                                        cost_g[i] -= a-b
                                if self.players[(player.place + 1) % 6].all_resources()[4+i]:
                                    a = cost_g[i]
                                    b = self.players[(player.place + 1) % 6].all_resources()[4+i]
                                    if a <= b:
                                        final[1] += a
                                        cost_g[i] -= a
                                    elif b < a:
                                        final[1] += a - b
                                        cost_g[i] -= a - b
                        if cost_g[i]:
                            if self.players[(player.place - 1) % 6].all_resources()[4+i]:
                                a = cost_g[i]
                                b = self.players[(player.place - 1) % 6].all_resources()[4+i]
                                if a <= b:
                                    final[0] += 2*a
                                    cost_g[i] -= a
                                elif b < a:
                                    final[0] += 2*(a - b)
                                    cost_g[i] -= a - b
                        if cost_g[i]:
                            if self.players[(player.place + 1) % 6].all_resources()[4+i]:
                                a = cost_g[i]
                                b = self.players[(player.place + 1) % 6].all_resources()[4+i]
                                if a <= b:
                                    final[1] += 2*a
                                    cost_g[i] -= a
                                elif b < a:
                                    final[1] += 2*(a - b)
                                    cost_g[i] -= a - b
                        if cost_g[i]:
                            return "no can do"
                finals.append(final)
            vals = [x+y for x, y in finals]
            if min(vals) > player.own_resources()[7]:
                return "no can do"

            return finals[vals.index(min(vals))]

    def cards_for_era(self, era):
        if era == 1:
            cards = np.random.shuffle(np.array([c.number for c in self.cards[:34]])).reshape((5,7))
        elif era == 2:
            cards = np.random.shuffle(np.array([c.number for c in self.cards[35:75]])).reshape((5,7))
        elif era == 3:
            cards = np.array([c.number for c in self.cards[76:97]])
            guilds = np.array([c.number for c in self.cards[98:107]])
            cards = np.random.shuffle(np.concatenate((cards,guilds[:6]))).reshape((5,7))
        return cards


if __name__ == "__main__":
    game = Game()
    game.load_cards()
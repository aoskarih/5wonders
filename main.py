import numpy as np
import random
from scipy.special import expit
import time
import itertools

preload_p = True

games_per_cycle = 10

# input neurons
in_neurons = 5*138+139
# neurons in hidden layer 20
hid_neurons = 256
# Mutation rate
mr = 0.001
# Weight magnitude
wm = 1
# num of actions
output_neurons = 139

cards = []
players = [None, None, None, None, None]

def load_cards():
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
                cards.append(Card(int(l[0]), l[1], [int(i) for i in cost], l[3],
                                       [int(i) for i in output], [int(i) for i in amount], l[6]))
            else:
                cards.append(Card(int(l[0]), l[1], [int(i) for i in cost], l[3],
                                       [int(i) for i in output], l[5], l[6]))
        else:
            cost = list(l[2])
            cards.append(Card(int(l[0]), l[1], [int(i) for i in cost], l[3], l[4], l[5], l[6]))



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
            self.switch_resource(self.out_type, self.amount)
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
        self.output[int(output)] = int(amount)

    def switch_resource(self, outputs, amount):
        for o in outputs:
            self.switch_output[int(o)] = int(amount)

    def stuff_for_cards(self, output, amount, peoples, color):
        if type(output) != int:
            output = output[0]
        number = 0
        pl = 0
        if peoples == 3:
            for p in range(3):
                pl = (self.owner + 1 - p) % 5
                index = 0
                for c in players[p].cards:
                    if c == 1:
                        if cards[index].color == color:
                            number += 1
                    index += 1
            self.output[int(output)] += int(amount)*number
        elif peoples == 2:
            for p in range(3):
                if p == 1:
                    continue
                pl = (self.owner + 1 - p) % 5
                index = 0
                for c in players[p].cards:
                    if c == 1:
                        if cards[index].color == color:
                            number += 1
                    index += 1
            self.output[int(output)] += int(amount)*number
        elif peoples == 1:
            index = 0
            for c in players[self.owner].cards:
                if c == 1:
                    if cards[index].color == color:
                        number += 1
                index += 1
            self.output[int(output)] += int(amount) * number

    def strategists_guild(self):
        number = 0
        pl = 0
        for p in range(3):
            if p == 1:
                continue
            pl = (self.owner + 1 - p) % 5
            index = 0
            number += players[pl].army_minuses
        self.output[9] += number


class Player:

    def __init__(self, place, wonder, neurons_in, neurons_mid, neurons_out,
                 w1=None, w2=None, w3=None, b1=None, b2=None, b3=None):
        self.place = place
        self.cards = np.zeros(138) 
        self.wonder = wonder
        self.money = 3
        self.armies = 0
        self.army_points = 0
        self.army_minuses = 0
        self.minuses = 0
        self.pluses = 0
        self.res_vectors = []
        self.wonder_cards = []
        self.neurons_mid = neurons_mid
        
        if w1 is not None:
            self.neurons_mid = int(neurons_mid+random.randint(-1, 1))
            self.w1 = np.clip(np.resize(w1, (self.neurons_mid, neurons_in)) + np.random.uniform(-mr, mr, (self.neurons_mid, neurons_in)), -wm/4, wm/4)
            #self.w2 = np.clip(w2 + np.random.uniform(-mr, mr, (self.neurons_mid, neurons_mid)), -wm, wm)
            self.w3 = np.clip(np.resize(w3, (neurons_out, self.neurons_mid)) + np.random.uniform(-mr, mr, (neurons_out, self.neurons_mid)), -wm/4, wm/4)
            self.b1 = np.clip(np.resize(b1, (self.neurons_mid)) + np.random.uniform(-mr, mr, self.neurons_mid), -wm/4, wm/4)
            #self.b2 = np.clip(b2 + np.random.uniform(-mr, mr, neurons_mid), -wm, wm)
            self.b3 = np.clip(b3 + np.random.uniform(-mr, mr, neurons_out), -wm/4, wm/4)
            for i in range(138):
                self.w1[i][i] = wm
            for i in range(138):
                self.w3[i][i] = wm
            return

        
        self.w1 = np.zeros((neurons_mid, neurons_in))
        #self.w2 = np.zeros((neurons_mid, neurons_mid))
        self.w3 = np.zeros((neurons_out, neurons_mid))
        self.b1 = np.zeros(neurons_mid)
        #self.b2 = np.random.randint(-wm, wm, size=neurons_mid)
        self.b3 = np.zeros(neurons_out)
        for i in range(138):
                self.w1[i][i] = wm
        for i in range(138):
            self.w3[i][i] = wm

    def add_card(self, card):
        self.cards[card] = 1

    def choose_card(self, a0):
        a1 = self.network_step(a0, self.w1, self.b1)
        #a2 = self.network_step(a1, self.w2, self.b2)
        output = self.network_step(a1, self.w3, self.b3) # a1 to a2
        return output

    def network_step(self, a, w, b):
        return expit(np.dot(w, a) + b)

    def switch_resources(self):
        switch_cards = []
        for i in range(len(self.cards)):
            if self.cards[i] and cards[i].action == "switch":
                switch_cards.append(cards[i])
        if switch_cards == []:
            return
        outputs = np.zeros((len(switch_cards), 8))
        for i in range(len(switch_cards)):
            switch_cards[i].do_action(self.place)
            outputs[i] = switch_cards[i].switch_output

        outputs = [np.nonzero(o)[0] for o in outputs]
        combinations = list(itertools.product(*outputs))
        for c in combinations:
            res_vec = [0, 0, 0, 0, 0, 0, 0, 0]
            for n in c:
                res_vec[n] += 1
            self.res_vectors.append(res_vec)

    def all_resources(self):
        res = [0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(len(self.cards)):
            if self.cards[i] and game.cards[i].action == "switch":
                cards[i].do_action(self.place)
                res += cards[i].switch_output
        res += self.own_resources()
        return res

    def own_resources(self):
        res = np.array([0, 0, 0, 0, 0, 0, 0, 0])

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
            if card:
                cards[int(card)].do_action(self.place)
                out = cards[int(card)].output[:7]
                out.append(0)
                res += out
        for card in self.cards[12:14]:
            if card:
                cards[int(card)].do_action(self.place)
                out = cards[int(card)].output[:7]
                out.append(0)
                res += out
        for card in self.cards[35:48]:
            if card:
                cards[int(card)].do_action(self.place)
                out = cards[int(card)].output[:7]
                out.append(0)
                res += out
        res[7] = self.money
        return res


class Game:
    
    wonders = ["alexandria_a", "aleksandria_b", "babylon_a", "babylon_b",
               "ephesos_a", "ephesos_b", "gizah_a", "gizah_b", "rhodos_a", "rhodos_b"]
    points = [0, 0, 0, 0, 0]
    real_points = [0, 0, 0, 0, 0]

    def __init__(self, w1=None, w2=None, w3=None, b1=None, b2=None, b3=None, neurons_mid=hid_neurons):
        random.shuffle(self.wonders)
        for i in range(5):
            if w1 is not None:
                players[i] = Player(i, self.wonders[i], in_neurons, neurons_mid, output_neurons,
                                           w1=w1, w2=w2, w3=w3, b1=b1, b2=b2, b3=b3)
            else:
                players[i] = Player(i, self.wonders[i], in_neurons, hid_neurons, output_neurons)
            for card in cards:
                if players[i].wonder in card.name:                    
                    players[i].wonder_cards.append(card.number)

    def game_cycle(self):
        random.shuffle(self.wonders)
        for p in players:
            p.cards = np.zeros(138)
            p.wonder = self.wonders[p.place]
            p.money = 3
            p.armies = 0
            p.army_minuses = 0
            p.army_points = 0
            p.pluses = 0
            p.minuses = 0
            p.res_vectors = []
            p.wonder_cards = []
        for era in range(3):
            self.era(era+1)
        self.point_calc()
        return self.points, self.real_points

    def point_calc(self):
        for p in players:
            science = [0, 0, 0]
            points = 0
            points += p.army_points
            points -= p.army_minuses
            for i in range(138):
                if p.cards[i]:
                    cards[i].do_action(p.place)
                    points += cards[i].output[9]                    
                    science[0] += cards[i].output[10]
                    science[1] += cards[i].output[11]
                    science[2] += cards[i].output[12]

            if p.cards[115] or p.cards[119]:
                if p.cards[107]:
                    sets = min(science)
                    points += 7*sets
                    points += science[0]*science[0]
                    points += science[1]*science[1]
                    points += science[2]*science[2]
            
            points += np.floor(p.money/3)
            self.real_points[p.place] = points
            points -= p.minuses
            points += p.pluses
            self.points[p.place] = points
        #print(self.real_points)

    def era(self, era):
        cards_for_era = self.cards_for_era(era)
        turn = 0
        while turn < 6:
            used_cards = []
            cards_to_play = [0, 0, 0, 0, 0]
            costs = [0, 0, 0, 0, 0]
            for p in players:
                cards_in_hand = cards_for_era[(p.place+turn)%5]
                available, costs[(p.place+turn)%5] = self.input_dat(p.place, cards_in_hand, p.wonder)
                card_weights = p.choose_card(available)
                card_to_be_played = card_weights.argmax()
                cards_to_play[(p.place+turn)%5] = card_to_be_played
            for p in players:
                cards_in_hand = cards_for_era[(p.place+turn)%5]
                card_to_be_played = cards_to_play[(p.place+turn)%5]
                if card_to_be_played in cards_in_hand and card_to_be_played != 138:
                    cost = "no can do"
                    for c in costs[(p.place+turn)%5]:
                        if c[1] == card_to_be_played:
                            cost = c[0]
                            break
                    if cost == "no can do":
                        # print("strange")
                        card = cards_in_hand[0]
                        cards_for_era[(p.place + turn)%5].remove(card)
                        p.money += 3
                        p.minuses += 10
                        continue
                    cards[card_to_be_played].do_action(p.place)
                    if cards[card_to_be_played].output[7]:
                        p.money += cards[card_to_be_played].output[7]
                    elif cards[card_to_be_played].output[8]:
                        p.money += cards[card_to_be_played].output[8]
                    p.add_card(card_to_be_played)
                    if card_to_be_played < 108:
                        cards_for_era[(p.place+turn)%5].remove(card_to_be_played)
                    else:
                        cards_for_era[(p.place + turn)%5].remove(cards_in_hand[0])
                    p.money -= sum(cost)
                    p.pluses += 5
                    players[(p.place - 1) % 5].money += cost[0]
                    players[(p.place + 1) % 5].money += cost[1]
                    if cards[card_to_be_played].cost[7] != 0:
                        p.money -= cards[card_to_be_played].cost[7]
                elif card_to_be_played == 138:
                    p.pluses += 5
                    card = cards_in_hand[0]
                    cards_for_era[(p.place + turn)%5].remove(card)
                    p.money += 3
                else:
                    card = cards_in_hand[0]
                    cards_for_era[(p.place + turn)%5].remove(card)
                    # p.money += 3
                    p.minuses += 5
                    
                if p.cards[118] and turn == 5:
                    p.money += 3
                # print(p.place, turn, era)
                if p.place == 4:
                    break
            turn += 1
        for p in players:

            if players[(p.place - 1) % 5].armies > p.armies:
                p.army_minuses += 1
            elif players[(p.place - 1) % 5].armies == p.armies:
                pass
            else:
                p.army_points += era*2-1

            if players[(p.place + 1) % 5].armies > p.armies:
                p.army_minuses += 1
            elif players[(p.place + 1) % 5].armies == p.armies:
                pass
            else:
                p.army_points += era*2-1

    def input_dat(self, place, cards_in_hand, wonder):

        input_dat = np.zeros((139))
        input_dat[138] = 1
        costs = []
        for card in cards_in_hand:
            cost = self.payment(card, players[place])
            costs.append([cost, card])
            if cost == "no can do":
                input_dat[card] = 0
            elif sum(cost) > players[place].money:
                input_dat[card] = 0
            else:
                input_dat[card] = 1

        for w in players[place].wonder_cards:
            cost = self.payment(w, players[place])
            if cost == "no can do":
                input_dat[w] = 0
            elif sum(cost) > players[place].money:
                input_dat[card] = 0
            else:
                input_dat[card] = 1

        for i in range(5):
            input_dat = np.concatenate((input_dat, players[(place + i) % 5].cards))

        return input_dat, costs

    def payment(self, card, player):
        cost = cards[card].cost
        cost = cost-player.own_resources()
        cost = cost.clip(min=0)
        if cost[7] != 0:
            return "no can do"
        if np.all(cost == 0):
            return [0, 0]
        finals = []
        player.switch_resources()
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
                                if players[(player.place - 1) % 5].all_resources()[i]:
                                    a = cost_b[i]
                                    b = players[(player.place - 1) % 5].all_resources()[i]
                                    if a <= b:
                                        final[0] += a
                                        cost_b[i] -= a
                                    elif b < a:
                                        final[0] += a-b
                                        cost_b[i] -= a-b
                        if cost_b[i]:
                            if player.cards[27]:
                                if players[(player.place + 1) % 5].all_resources()[i]:
                                    a = cost_b[i]
                                    b = players[(player.place + 1) % 5].all_resources()[i]
                                    if a <= b:
                                        final[1] += a
                                        cost_b[i] -= a
                                    elif b < a:
                                        final[1] += a - b
                                        cost_b[i] -= a - b
                        if cost_b[i]:
                            if players[(player.place - 1) % 5].all_resources()[i]:
                                a = cost_b[i]
                                b = players[(player.place - 1) % 5].all_resources()[i]
                                if a <= b:
                                    final[0] += 2*a
                                    cost_b[i] -= a
                                elif b < a:
                                    final[0] += 2*(a - b)
                                    cost_b[i] -= a - b
                        if cost_b[i]:
                            if players[(player.place + 1) % 5].all_resources()[i]:
                                a = cost_b[i]
                                b = players[(player.place + 1) % 5].all_resources()[i]
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
                                if players[(player.place - 1) % 5].all_resources()[4+i]:
                                    a = cost_g[i]
                                    b = players[(player.place - 1) % 5].all_resources()[4+i]
                                    if a <= b:
                                        final[0] += a
                                        cost_g[i] -= a
                                    elif b < a:
                                        final[0] += a-b
                                        cost_g[i] -= a-b
                                if players[(player.place + 1) % 5].all_resources()[4+i]:
                                    a = cost_g[i]
                                    b = players[(player.place + 1) % 5].all_resources()[4+i]
                                    if a <= b:
                                        final[1] += a
                                        cost_g[i] -= a
                                    elif b < a:
                                        final[1] += a - b
                                        cost_g[i] -= a - b
                        if cost_g[i]:
                            if players[(player.place - 1) % 5].all_resources()[4+i]:
                                a = cost_g[i]
                                b = players[(player.place - 1) % 5].all_resources()[4+i]
                                if a <= b:
                                    final[0] += 2*a
                                    cost_g[i] -= a
                                elif b < a:
                                    final[0] += 2*(a - b)
                                    cost_g[i] -= a - b
                        if cost_g[i]:
                            if players[(player.place + 1) % 5].all_resources()[4+i]:
                                a = cost_g[i]
                                b = players[(player.place + 1) % 5].all_resources()[4+i]
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
        return "no can do"

    def cards_for_era(self, era):
        if era == 1:
            cards_era = np.array([c.number for c in cards[:35]])
            np.random.shuffle(cards_era)
            cards_era = cards_era.reshape((5,7))
        elif era == 2:
            cards_era = np.array([c.number for c in cards[35:70]])
            np.random.shuffle(cards_era)
            cards_era = cards_era.reshape((5,7))
        elif era == 3:
            cards_era = np.array([c.number for c in cards[70:98]])
            guilds = np.array([c.number for c in cards[99:108]])
            np.random.shuffle(guilds)
            cards_era = np.concatenate((cards_era, guilds[:7]))
            np.random.shuffle(cards_era)
            cards_era = cards_era.reshape((5,7))
        return cards_era.tolist()


def training_cycle(p=None):
    t1 = time.time()
    cycle_points = [[] for i in range(games_per_cycle)]
    cycle_real_points = [[]] * games_per_cycle
    if p is not None:
        print()
        game = Game(w1=p.w1, w3=p.w3, b1=p.b1, b3=p.b3, neurons_mid=p.neurons_mid) # w2=p.w2, , , b2=p.b2
    else:
        game = Game()
    for i in range(games_per_cycle):
        points, real_points = game.game_cycle()
        print(real_points)
        cycle_points[i] = points
        cycle_real_points[i] = real_points
    t2 = time.time()
    print(cycle_real_points)
    point_avg = [0, 0, 0, 0, 0]
    real_point_avg = [0, 0, 0, 0, 0]
    for i in range(games_per_cycle):
        for j in range(5):
            point_avg[j] += cycle_points[i][j] 
            real_point_avg[j] += cycle_real_points[i][j]
    point_avg = [x/games_per_cycle for x in point_avg]
    real_point_avg = [x/games_per_cycle for x in real_point_avg]
    p = players[point_avg.index(max(point_avg))]
    return p, t2-t1, point_avg, real_point_avg

def save_state(p, n):
    nw1, nw3, nb1, nb3 = "w1_"+str(n), "w3_"+str(n), "b1_"+str(n), "b3_"+str(n)
    np.save(nw1, p.w1)
    np.save(nw3, p.w3)
    np.save(nb1, p.b1)
    np.save(nb3, p.b3)

if __name__ == "__main__":
    cycle_number = 0
    p = None
    t_start = time.time()
    if input("preload file? (y/n): ") == 'y':
        preload_p = True
    else:
        preload_p = False

    if preload_p:
        nm = input("File num: ")
        w1 = np.load("w1_"+nm+".npy")
        w3 = np.load("w3_"+nm+".npy")
        b1 = np.load("b1_"+nm+".npy")
        b3 = np.load("b3_"+nm+".npy")
        p = Player(0, 0, in_neurons, hid_neurons, output_neurons,
        w1=w1, w3=w3, b1=b1, b3=b3)
    load_cards()
    while True:
        if p is not None:
            p, t, points, real_score = training_cycle(p)
        else:
            p, t, points, real_score = training_cycle()
        cycle_number += 1
        if cycle_number % 5000 == 0:
            print("state saved, time since beginning: " + str("{0:.1f}".format(((time.time()-t_start)/60)))
                  + " minutes")
            save_state(p, cycle_number)

        
        print("game "+ str(cycle_number) +" lasted: " + str("{0:.3f}".format(t)) + " seconds")
        #print(plus)
        print("Best score: " + str(int(max(real_score)))+ " ("+str(p.pluses/5) + ")")
        print("Average score: " + str(sum(real_score)/len(real_score)))
        print("Hidden neurons: " + str(p.neurons_mid))

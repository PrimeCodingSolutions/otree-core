from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, widgets
)
import json
import networkx as nx
from networkx.readwrite import json_graph
from operator import itemgetter
from itertools import groupby
import numpy as np
import pandas as pd
import random
from itertools import chain
from .questions import make_question, question_order
from django.db import models as django_models
from otree.models import Participant
df = pd.read_excel("bad_influence/fornavne.xlsx")
unisex = df['unisex'].dropna().tolist()
girls_names = df['girls'].dropna().tolist()
boys_names = df['boys'].dropna().tolist()


class Constants(BaseConstants):
    name_in_url = 'bad_influence'
    players_per_group = None
    num_rounds = len(question_order)
    num_initial_friends = 3
    high_bonus = 10
    low_bonus = 5
    hub_fraction = 0.4
    round_length = 120
    koen = random.choice([True, False])


class Subsession(BaseSubsession):
    full_network = models.LongStringField()
    consensus = models.FloatField()

    def print_graph_stats(self, G):
        print('average clustering: ', nx.average_clustering(G))
        degrees = [val for (node, val) in G.degree()]
        print('average degree: ', sum(degrees) / float(len(G)))
        print('density: ', nx.density(G))
        print('assortativity coefficient (Pearson\'s rho): ', nx.degree_pearson_correlation_coefficient(G))
        print('(should be negative according to Gonzalez et al., 2007)')
        import operator
        x = nx.betweenness_centrality(G)
        sorted_x = sorted(x.items(), key=operator.itemgetter(1))
        print('betweenness centrality', sorted_x)
        x = nx.degree_centrality(G)
        sorted_x = sorted(x.items(), key=operator.itemgetter(1))
        print('degree centrality:', sorted_x)
        x = nx.eigenvector_centrality(G)
        sorted_x = sorted(x.items(), key=operator.itemgetter(1))
        print('eigenvector centrality:', sorted_x)
        x = nx.katz_centrality(G)
        sorted_x = sorted(x.items(), key=operator.itemgetter(1))
        print('Katz centrality:', sorted_x)
        x = nx.closeness_centrality(G)
        sorted_x = sorted(x.items(), key=operator.itemgetter(1))
        print('closeness centrality:', sorted_x)
        print('\n')

    def creating_session(self):
        self.get_groups()[0].question = question_order[self.round_number]

        # generate full network
        G = nx.generators.powerlaw_cluster_graph(self.session.num_participants, Constants.num_initial_friends, 0.2)

        # label the (hub_fraction)% most highly connected players as being hubs
        # and assign default color attributes and default choices:
        node_and_degree = sorted(G.degree(), key=itemgetter(1), reverse=True)
        hubs_in_graph, _ = map(list,
                               zip(*node_and_degree[:int(self.session.num_participants * Constants.hub_fraction)]))
        normal_in_graph, _ = map(list,
                                 zip(*node_and_degree[int(self.session.num_participants * Constants.hub_fraction):]))

        times_has_been_hub = [(p.id_in_group, p.count_times_has_been_hub()) for p in self.get_players()]
        random.shuffle(times_has_been_hub)
        times_has_been_hub = sorted(times_has_been_hub, key=itemgetter(1))

        hubs_for_this_round, _ = map(list, (
            zip(*times_has_been_hub[:int(self.session.num_participants * Constants.hub_fraction)])))
        normal_for_this_round, _ = map(list, zip(
            *times_has_been_hub[int(self.session.num_participants * Constants.hub_fraction):]))

        random.shuffle(hubs_for_this_round)
        random.shuffle(normal_for_this_round)

        relabels = {
            r[0]: r[1] for r in chain(
                zip(hubs_in_graph, hubs_for_this_round),
                zip(normal_in_graph, normal_for_this_round)
            )}

        G = nx.relabel_nodes(G, lambda x: relabels.get(x))


        # generate names:
        if self.round_number == 1:
            self.session.vars['uni'] = json.dumps(random.sample(unisex, self.session.num_participants))
            self.session.vars['girls'] = json.dumps(random.sample(girls_names, self.session.num_participants))
            self.session.vars['boys'] = json.dumps(random.sample(boys_names, self.session.num_participants))

        for p in self.get_players():
            if p.id_in_group in hubs_for_this_round:
                p.hub = p.choice = G.nodes[p.id_in_group]['choice'] = True
                G.nodes[p.id_in_group]['preference'] = True
            else:
                p.hub = p.choice = G.nodes[p.id_in_group]['choice'] = False
                G.nodes[p.id_in_group]['preference'] = False
            G.nodes[p.id_in_group]['name'] = 'dummy'
            G.nodes[p.id_in_group]['exp_score'] = 0

        # generate ego-networks to be displayed
        for p in self.get_players():
            ego_net = json_graph.node_link_data(nx.ego_graph(G, p.id_in_group))
            p.ego_network = json.dumps(ego_net)
            p.number_of_friends = len([i['id'] for i in ego_net['nodes']]) - 1

        # save full network
        self.full_network = json.dumps(json_graph.node_link_data(G))
        self.get_groups()[0].graph = self.full_network

        # save level of color consensus:
        color_dict = nx.get_node_attributes(G, 'choice')
        color_array = sorted(color_dict.values())  # array with blues first
        color_hist = [len(list(group)) for key, group in groupby(color_array)]

    def vars_for_admin_report(self):
        group = self.get_groups()[0]
        data = [{
            "graph": json_graph.node_link_data(group.get_graph()),
            "history": json.loads(group.history),
            "question": make_question(group, False, True, False),
            "start_time": group.round_start_time,
            "end_time": group.round_end_time,
        } for group in group.in_all_rounds()]

        rankings = []

        for player in group.get_players():


        for p in self.get_players():
            p.navn = p.participant.vars["name"]
            p.stubborn_total = sum([player.stubborn for player in p.in_all_rounds()])
            p.opinion_change_total = sum([player.opinion_change for player in p.in_all_rounds()])
            p.number_of_friends_total = sum([player.number_of_friends for player in p.in_all_rounds()])
            p.points_total = sum([player.points for player in p.in_all_rounds()])
            p.fulgt_flertallet_pct = 100 * sum(
                [1 for player in p.in_all_rounds() if player.points != 0]) / Constants.num_rounds
            p.fulgt_preference_pct = 100 * sum(
                [1 for player in p.in_all_rounds() if player.hub == player.choice]) / Constants.num_rounds
            rankings.append((p.navn, p.points_total, p.fulgt_flertallet_pct,
                             p.fulgt_preference_pct, np.around(p.stubborn_total, 1),
                             p.number_of_friends_total, p.opinion_change_total))
            print(p.navn)

        return {
            "data": json.dumps(data),
            "id_in_group": -1,
            'rankings': sorted(rankings, key=lambda x: x[1], reverse=True),
            'points_total': p.points_total
        }


class Group(BaseGroup):
    history = models.LongStringField(initial=json.dumps([]))
    graph = models.LongStringField()
    consensus = models.FloatField()
    question = models.StringField()
    round_start_time = models.FloatField()
    round_end_time = models.FloatField()
    choice = models.BooleanField()

    def add_to_history(self, to_add):
        history = json.loads(self.history)
        history.append(to_add)
        self.history = json.dumps(history)
        self.save()

    def get_graph(self):
        graph = json_graph.node_link_graph(json.loads(self.graph))
        for p in self.get_players():
            graph.nodes[p.id_in_group]['choice'] = p.choice
            graph.nodes[p.id_in_group]['name'] = p.set_names()
            graph.nodes[p.id_in_group]['exp_score'] = p.get_expected_score()
        return graph

    # def set_name_in_graph(self):
    #     graph = json_graph.node_link_graph(json.loads(self.graph))
    #     for p in self.get_players():
    #         graph.nodes[p.id_in_group]['name'] = p.navn
    #     return graph

    def get_consensus(self):
        graph = self.get_graph()
        color_dict = nx.get_node_attributes(graph, 'choice')
        color_array = sorted(color_dict.values())  # array with blues first
        color_hist = [len(list(group)) for key, group in groupby(color_array)]
        color_freq = np.array(color_hist) / np.sum(np.array(color_hist))
        return max(color_freq)

    def get_minority_ratio(self):
        graph = self.get_graph()
        choices = nx.get_node_attributes(graph, 'choice')
        return sum(choices.values()) / len(choices)

    def set_graph(self, graph):
        self.graph = json.dumps(json_graph.node_link_data(graph))

    def get_channel_group_name(self):
        return 'network_voting_group_{}'.format(self.pk)

    def get_egonetwork(self, id):
        for p in self.get_players():
            if p.id_in_group == id:
                E = json.loads(p.ego_network)
                return [i['id'] for i in E['nodes']]

    def stubborness(self):
        history = json.loads(self.history)
        stubborn = {}
        start_time = history[0]['time']
        final_time = history[-1]['time']
        total_time = final_time - start_time
        if total_time < Constants.round_length - 1:  # if people are finished before 2 mins, create a new entry and reset times:
            # print('Oh, too much time!')
            endpoint = json.loads(json.dumps(history[-1]))
            endpoint.update({'time': start_time + Constants.round_length})
            history.append(endpoint)
            final_time = history[-1]['time']
            total_time = final_time - start_time

        for i in range(1, len(history)):  # every time someone changes her opinion...
            time_interval = history[i]['time'] - history[i - 1]['time']  # get the time interval to last time
            try:
                id = history[i]['choice']['id']  # find id of who changed her mind
            except:
                id = 0
            for p in self.get_players():
                (stubborness, opinion_changes) = stubborn.get(p.id_in_group,
                                                              (total_time, 0))  # retrieve or initialize dict
                choice = next(item for item in history[i]['nodes'] if item["id"] == p.id_in_group)[
                    'choice']  # what is the choice
                preference = next(item for item in history[i]['nodes'] if item["id"] == p.id_in_group)[
                    'preference']  # what is the preference

                if p.id_in_group == id and i != (len(history) - 1):
                    opinion_changes += 1  # counts the number of opinion changes (not the last because it was artificially created)

                # load the ego-graph of player p in order to find her friends:
                E = json.loads(p.ego_network)
                friends = [i['id'] for i in E['nodes']]

                # count the friend choices
                tot = []
                for friend in friends:
                    tot.append(sum([item['choice'] for item in history[i]['nodes'] if item['id'] == friend]))

                # decrease sutbborness with time interval if condition not met:
                if (preference == True and choice == True and sum(tot) < len(friends) / 2) or (
                        preference == False and choice == False and sum(tot) > len(friends) / 2):
                    pass
                else:
                    stubborness -= time_interval

                # save
                stubborn[p.id_in_group] = (stubborness, opinion_changes)

        # give each player her stubborness value and her count of opinion changes:
        for p in self.get_players():
            p.stubborn = np.around(stubborn[p.id_in_group][0], 1)
            p.opinion_change = stubborn[p.id_in_group][1]


class Player(BasePlayer):
    ego_network = models.LongStringField()
    friends = models.LongStringField()
    hub = models.BooleanField()
    choice = models.BooleanField(
        choices=[
            [True, 'Rød'],
            [False, 'Blå'],
        ],
    )
    choice_str = models.StringField()
    preference_str = models.StringField()
    gender = models.BooleanField(default=Constants.koen)
    number_of_friends = models.IntegerField()
    spg = models.LongStringField()
    last_choice_made_at = models.IntegerField()
    stubborn = models.FloatField(initial=0)
    opinion_change = models.IntegerField(initial=0)
    stubborn_total = models.FloatField(initial=0)
    opinion_change_total = models.IntegerField(initial=0)
    number_of_friends_total = models.IntegerField(initial=0)
    chat_color = models.LongStringField()
    points = models.IntegerField(initial=0)
    points_total = models.IntegerField(initial=0)
    fulgt_flertallet_pct = models.FloatField(initial=0)
    fulgt_preference_pct = models.FloatField(initial=0)
    navn = models.StringField(widget=widgets.RadioSelectHorizontal())
    expected_score = models.IntegerField(initial=0)


    def navn_choices(self):
        uni = json.loads(self.session.vars['uni'])
        girl = json.loads(self.session.vars['girls'])
        boy = json.loads(self.session.vars['boys'])
        choices = [uni[self.id_in_group - 1], girl[self.id_in_group - 1], boy[self.id_in_group - 1]]
        return choices

    def set_names(self):
        if self.round_number == 1:
            self.participant.vars['name'] = self.navn
        else:
            self.navn = self.participant.vars['name']
        return self.navn

    def get_personal_channel_name(self):
        return '{}-{}'.format(self.id_in_group, self.id)

    def set_points(self):
        # print('round ', self.round_number)
        # print(json_graph.node_link_data(self.group.get_graph()))
        all_choices = [p.choice for p in self.group.get_players()]
        self.group.choice = sum(all_choices) > len(all_choices) / 2
        if sum(all_choices) > len(all_choices) / 2:  # if hubs have gotten the majority
            if self.hub == True and self.choice == True:  # if you are a hub and chooses likewise
                self.points = 3 + self.number_of_friends
            elif self.hub == False and self.choice == True:  # if you are NOT a hub but go with the majority
                self.points = 3  # self.number_of_friends
            else:
                self.points = 0
        elif sum(all_choices) < len(all_choices) / 2:  # if hubs have NOT gotten the majority
            if self.hub == False and self.choice == False:  # if you are NOT a hub and chooses likewise
                self.points = 3 + self.number_of_friends
            elif self.hub == True and self.choice == False:  # if you are a hub but go with the majority
                self.points = 3  # self.number_of_friends
            else:
                self.points = 0
        else:  # if there is a tie:
            self.points = 0

    def get_expected_score(self):
        friends = self.get_friends()
        sum_choices = sum([friend.choice for friend in self.get_others_in_group() if friend.id_in_group in friends])
        if self.hub == False:
            if sum_choices < len(friends)/2 and self.choice == False:
                self.expected_score = 3 + len(friends) - 1
            elif sum_choices >= len(friends)/2 and self.choice == False:
                self.expected_score = 0
            elif self.choice == True and sum_choices <= len(friends)/2:
                self.expected_score = 0
            else:
                self.expected_score = 3
        if self.hub == True:
            if sum_choices < len(friends)/2 and self.choice == False:
                self.expected_score = 3
            elif sum_choices >= len(friends)/2 and self.choice == False:
                self.expected_score = 0
            elif self.choice == True and sum_choices <= len(friends)/2:
                self.expected_score = 0
            else:
                self.expected_score = 3 + len(friends) - 1
        # print(self.id_in_group, self.choice, self.hub, sum_choices, len(friends), self.expected_score)
        return self.expected_score

    def get_question_title(self):
        self.spg = make_question(self.group, self.hub, self.gender, self.number_of_friends)['title']

    def get_preference_text(self):
        if self.hub == 0:
            self.preference_str = make_question(self.group, self.hub, self.gender, self.number_of_friends)['majority_choice']
        else:
            self.preference_str = make_question(self.group, self.hub, self.gender, self.number_of_friends)['minority_choice']

    def get_choice_text(self):
        if self.choice == 0:
            self.choice_str = make_question(self.group, self.hub, self.gender, self.number_of_friends)['majority_choice']
        else:
            self.choice_str = make_question(self.group, self.hub, self.gender, self.number_of_friends)['minority_choice']

    def get_friends(self):
        E = json.loads(self.ego_network)
        return [i['id'] for i in E['nodes']]

    def chat_nickname(self):
        return 'Spiller {}'.format(self.id_in_group)

    def chat_configs(self):
        configs = []
        friends = self.get_friends()
        for friend in self.get_others_in_group():
            if friend.id_in_group in friends:
                if friend.id_in_group < self.id_in_group:
                    lower_id, higher_id = friend.id_in_group, self.id_in_group
                else:
                    lower_id, higher_id = self.id_in_group, friend.id_in_group
                configs.append({
                    # make a name for the channel that is the same for all
                    # channel members. That's why we order it (lower, higher)
                    'channel': '{}-{}-{}'.format(self.group.id, lower_id, higher_id),
                    'label': 'Chat med {}'.format(friend.chat_nickname())
                })
        return configs

    def count_times_has_been_hub(self):
        return sum([p.hub for p in self.in_previous_rounds()])

    def hex_color(self):
        random_hex = lambda: random.randint(0, 255)
        self.chat_color = "%02X%02X%02X".format(random_hex(), random_hex(), random_hex())


class Message(models.Model):
    content = models.TextField()
    timestamp = django_models.DateTimeField(auto_now=True)
    player = models.ForeignKey('Player', on_delete=models.CASCADE, null=True)
    chat_id = models.IntegerField()
    group = models.ForeignKey('Group', on_delete=models.CASCADE, null=True)
    player_name = models.StringField()

    @staticmethod
    def last_30_messages():
        last_30 = Message.objects.order_by('-timestamp')[:30]
        return reversed(last_30)

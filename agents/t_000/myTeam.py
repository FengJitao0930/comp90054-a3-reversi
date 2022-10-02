import queue
from collections import deque

from Reversi.reversi_model import ReversiGameRule
from template import Agent
import random
import time

Winner_Point = [(0,0),(0,7),(7,0),(7,7)]
Lose_point = [(1,1), (1,6),(6,1), (6,6)]


class myAgent(Agent):
    def __init__(self,_id):
        super().__init__(_id)
        self.myAgent_game = ReversiGameRule(2)

    def getActions(self, state, agentId):
        return self.myAgent_game.getLegalActions(state,agentId)


    def get_next_state(self, state, action, agentId):
        nextState = self.myAgent_game.generateSuccessor(state, action, agentId)
        return nextState
    def get_next_state_score(self, nextstate, agentId):
        nextStateScore = self.myAgent_game.calScore(nextstate, agentId)
        return nextStateScore

    def EndingGame(self, state):
       return self.getActions(state, self.id) == ["Pass"] and self.getActions(state, 1-self.id) == ["Pass"]

    def findMaxWinnerPoint(self, points, actions):
        choose_action = []
        for item in points:
            for action in actions:
                if item[0] == action[0] and item[1] == action[1]:
                    choose_action.append(item)

        return choose_action

    def reducelostPoint(self, points, actions):

        choose_action_set = set()
        for action in actions:
            for item in points:
                if item[0] != action[0] and item[1] != action[1]:
                    choose_action_set.add(action)
        choose_action = list(choose_action_set)
        return choose_action

    def time_consume(self, start_time):
        return time.time() - start_time

    def avoid_must_lose_case(self, actions, game_state):
        lose_point = [0, 7]

        current_max_score = -1
        result = None
        for action in actions:
                y, x = action
                current_state_color = game_state.agent_colors
                if y == lose_point[0] or y == lose_point[1]:
                    nextState = self.get_next_state(game_state, action,self.id)
                    nextStateScore = self.get_next_state_score(nextState, self.id)
                    count_agent_single = 0
                    count_agent_double = 0
                    if (x != 0 and x != 7):
                        for i in range(1,6):
                            if i % 2 == 1 and nextState.board[i][y] == current_state_color:
                                count_agent_single += 1
                            else:
                                count_agent_double += 1
                        if count_agent_double == 3 or count_agent_double == 3 and not count_agent_double + count_agent_single == 6:
                            continue
                    else:
                        if nextStateScore > current_max_score:
                            current_max_score = nextStateScore
                            result = action

                elif x == lose_point[0] or x == lose_point[1]:
                    nextState = self.get_next_state(game_state, action,self.id)
                    nextStateScore = self.get_next_state_score(nextState, self.id)
                    count_agent_single = 0
                    count_agent_double = 0

                    if (y != 0 and y != 7):
                        for i in range(1, 6):
                            if i % 2 == 1 and nextState.board[x][i] == current_state_color:
                                count_agent_single += 1
                            else:
                                count_agent_double += 1

                        if count_agent_double == 3 or count_agent_single == 3 and not count_agent_double + count_agent_single == 6:
                            continue
                    else:
                        if nextStateScore > current_max_score:
                            current_max_score = nextStateScore
                            result = action


        return result

    def find_max_score_action(self,state, reverse_next_actions, start_time):
        max_score = -1
        action = None
        for reverse_next_action in reverse_next_actions:
            if self.time_consume(start_time) > 1:
                break
            next_action_State = self.get_next_state(state, reverse_next_action, 1 - self.id)
            nextStateScore = self.get_next_state_score(next_action_State, 1 - self.id)
            if max_score < nextStateScore:
                max_score = nextStateScore
                action = reverse_next_action
        return action

    def SelectAction(self, actions, game_state):
        start_time = time.time()

        self.myAgent_game.agent_colors = game_state.agent_colors

        Queue = deque([(game_state, [])])

        max_value = -1

        result = random.choice(actions)
        case_action = self.findMaxWinnerPoint(Winner_Point, actions)

        if len(case_action) != 0:
            find_max_action_value = -1
            best_action = None
            for action in case_action:
                next_state = self.get_next_state(game_state,action,self.id)
                next_state_score = self.get_next_state_score(next_state,self.id)
                if next_state_score>find_max_action_value:
                    best_action = action
            return best_action

        if not self.avoid_must_lose_case(actions, game_state) == None:
            return self.avoid_must_lose_case(actions, game_state)


        while self.time_consume(start_time) < 1 and not (len(Queue) == 0):

            state, path = Queue.pop()

            nextActions = self.getActions(game_state, self.id)

            case_action = self.findMaxWinnerPoint(Winner_Point, nextActions)
            if len(case_action) != 0:
                nextActions = case_action

            case_action = self.reducelostPoint(Lose_point, nextActions)
            if len(case_action) != 0:
                nextActions = case_action

            for action in nextActions:
                if self.time_consume(start_time) > 1:
                    break
                path = path + [action]
                nextState = self.get_next_state(state, action, self.id)
                nextStateScore = self.get_next_state_score(nextState, self.id)

                # choose the max
                if self.EndingGame(nextState):
                    if max_value < nextStateScore:
                        max_value = nextStateScore
                        result = path[0]
                        continue

                max_score = -1
                reverse_next_actions = self.getActions(nextState, 1-self.id)

                for reverse_next_action in reverse_next_actions:
                    if self.time_consume(start_time) > 1:
                        break
                    next_action_State = self.get_next_state(nextState, reverse_next_action, 1 - self.id)
                    nextStateScore = self.get_next_state_score(next_action_State, 1-self.id)
                    if max_score < nextStateScore:
                        max_score = nextStateScore
                        nextState = next_action_State
                # reverse_next_action = self.find_max_score_action(nextState, reverse_next_actions, start_time)
                nextState = self.get_next_state(nextState, reverse_next_action, 1 - self.id)

                Queue.appendleft((nextState, path + [reverse_next_action]))

        return result
    # def Timing(self, start_time):
    #     return time.time() - start_time
    #
    #
    #
    # def SelectAction(self,actions,game_state):
    #
    #     self.myAgent_game.agent_colors = game_state.agent_colors
    #     startTime = time.time()
    #     Queue = deque([(game_state, [])])
    #     max_value = -1
    #     solution = random.choice(actions)
    #     while self.Timing(startTime) < 1 and len(Queue) != 0:
    #         current_state, policy = Queue.popleft()
    #         satisfy_actions = self.myAgent_game.getLegalActions(current_state, self.id)
    #
    #         for action in satisfy_actions:
    #
    #             if self.Timing(startTime) > 1:
    #                 break
    #             next_state = self.myAgent_game.generateSuccessor(current_state, action, self.id)
    #             next_state_policy = policy + [action]
    #             next_state_score = self.myAgent_game.calScore(current_state, self.id)
    #
    #             if self.getLegalActions(next_state, self.id) == ["Pass"] and self.getLegalActions(next_state, 1-self.id) == ["Pass"]:
    #                 if max_value < next_state_score:
    #                     max_value = next_state_score
    #                     solution = policy[0]
    #                     break
    #
    #             reversed_actions = self.myAgent_game.getLegalActions(current_state, 1-self.id)
    #             reversed_action = reversed_actions[0]
    #             next_state = self.myAgent_game.generateSuccessor(next_state,reversed_action,1-self.id)
    #             Queue.append((next_state, next_state_policy))
    #
    #             # max_socre = -1
    #             # reverse_action_choice = []
    #             # for reversed_action in reversed_actions:
    #             #     if self.Timing(startTime) > 0.95:
    #             #         break
    #             #     reversed_next_score = self.myAgent_game.calScore(next_state, 1 - self.id)
    #             #     if reversed_next_score < max_socre:
    #             #         reverse_action_choice = reversed_action
    #             # next_state = self.myAgent_game.generateSuccessor(next_state, reverse_action_choice, 1-self.id)
    #             # Queue.append(next_state, policy + reverse_action_choice)
    #
    #     return solution

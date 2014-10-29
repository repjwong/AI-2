# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        """
        variables used:
        distance to closest food
        distance to active ghosts
        distance to scared ghost
        number of food pellets remaining
        number of power pellets remaining
        """
        currentScore = scoreEvaluationFunction(successorGameState)
        foodList = newFood.asList()
        numFood = len(foodList) #number of food pellets remaining
        numPower = len(successorGameState.getCapsules()) #number of power pellets remaining
        
        """distance to the closest food pellet"""
        distToClosestFood = 100     #changed, because 99999 was causing code to hang
        for food in foodList:
            mhDist = util.manhattanDistance(newPos, food)
            distToClosestFood = min(distToClosestFood, mhDist)
        
        """distance to the closest power pellet"""    
        distToClosestPower = 100    #same reason for change
        for power in successorGameState.getCapsules():
            distToClosestPower = min(distToClosestPower, (util.manhattanDistance(newPos, power)))
            
        if distToClosestPower == 100:   #incase there is no power pellet in example, elimintes this from equation
              distToClosestPower = 0
            
        activeGhosts, scaredGhosts = [], []
        
        """Distinguish between active and scared ghosts"""        
        for ghostState in newGhostStates:
            if not ghostState.scaredTimer:
                activeGhosts.append(ghostState)
            else:
                scaredGhosts.append(ghostState)
        
        """get the closest distance to active and scared ghosts"""
        distToClosestActiveGhost = 100      #read above
        for active in activeGhosts:
            distToClosestActiveGhost = min(util.manhattanDistance(active.getPosition(), newPos), distToClosestActiveGhost)
            if distToClosestActiveGhost == 0:
                distToClosestActiveGhost = 1 #prevents float division by zero
        
        distToClosestScaredGhost = 100      #why is this an issue
        for scared in scaredGhosts:
            distToClosestScaredGhost = min(util.manhattanDistance(scared.getPosition(), newPos), distToClosestScaredGhost)
        
       
             
        score = currentScore - (distToClosestFood) +  (distToClosestActiveGhost)
                   
                   
        # print (currentScore - (distToClosestFood) + abs(distToClosestActiveGhost - 2) )
       # print( "s" + str( currentScore - ((distToClosestFood)) + ((distToClosestActiveGhost) + 1 ) - (distToClosestPower - .5) ) )

        return score
        return successorGameState.getScore()

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        numAgents = gameState.getNumAgents()
        PACMAN = 0 #index of PACMAN
        
        def dispatch(gameState, index, depth):
            #when the index equals the number of ghosts, reset back to PACMAN and decrease the depth by 1
            if index == numAgents -1:
                depth -= 1
                index = PACMAN
            
            #Either PACMAN wins or the ghosts win or we have reached our depth so return the score   
            if gameState.isWin() or gameState.isLose() or depth == 0:
                return self.evaluationFunction(gameState)
            #max agent
            elif index == PACMAN:
                return max_value(gameState, index, depth)
            #min value
            else: return min_value(gameState, index, depth)
        
        """PACMAN"""    
        def max_value(gameState, agentIndex, depth):
            v = float("-inf")
            legalActions = gameState.getLegalActions(agentIndex)
            #evaluate each possible action for PACMAN
            for action in legalActions:
                successor = gameState.generateSuccessor(agentIndex, action)
                v = max(v, dispatch(successor, agentIndex + 1, depth)) #increase the agent index here
            return v
                
            
        """Ghosts"""    
        def min_value(gameState, agentIndex, depth):
            v = float("inf")
            legalActions = gameState.getLegalActions(agentIndex)
            #evaluate each possible action for a ghost
            for action in legalActions:
                successor = gameState.generateSuccessor(agentIndex, action)
                v = min(v, dispatch(successor, agentIndex+1, depth))
            return v
        #this runs first to start the original dispatch
        legalActions = gameState.getLegalActions(PACMAN)
        bestScore = float("-inf")
        bestAction = None
        
        for action in legalActions:
            successor = gameState.generateSuccessor(PACMAN, action)
            score = dispatch(successor, 1, self.depth) #first dispatch
            #the best score will be associated with an action
            if score > bestScore:
                bestScore = score
                bestAction = action
           
        return bestAction

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction


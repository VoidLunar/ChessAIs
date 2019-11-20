import json #Need this because my config files are in JSON
import time #Need this to get current time
import random #Need this for RNG
import sys #Need this for args
from Player import Player
from AI import play
#import cProfile

#==========Chess Stuff===========
white_pieces = ['P', 'B', 'N', 'R', 'Q']
black_pieces = ['p', 'b', 'n', 'r', 'q']
chess_piece_values = {
'k': 0,
'p': -1,
'b': -3,
'n': -3,
'r': -5,
'q': -9,
'K': 0,
'P': 1,
'B': 3,
'N': 3,
'R': 5,
'Q': 9}


def getSensorValues(board):
    sensorValues = {}
    pieces = board.piece_map()
    boardScore = 0
    for piece in pieces:
        symbol = pieces[piece].symbol()
        boardScore += chess_piece_values[symbol]
    sensorValues['B'] = boardScore
    if board.is_check():
        sensorValues['H'] = 50
    else:
        sensorValues['H'] = 0
    if board.is_checkmate():
        sensorValues['M'] = 50
    else:
        sensorValues['M'] = 0
    if board.is_game_over():
        #not draw if checkmate
        sensorValues['S'] = 50 - sensorValues['M']
    else:
        sensorValues['S'] = 0
    attackScore = 0
    for piece in pieces:
        symbol = pieces[piece].symbol()
        if symbol in white_pieces:
            attackScore += len(board.attacks(piece))
    sensorValues["A"] = attackScore
    return sensorValues



#=========GP Tree stuff=========
#lists with the functions for easy sampling
leafFunctions = ['B', 'C', 'M', 'S', 'A', 'H']
nonLeafFunctions = ['+', '-', '*', '/', 'RAND']
functions = ['B', 'C', 'M', 'S', 'A', 'H', '+', '-', '*', '/', 'RAND']

#node class
class GPNode:
    def __init__(self, function, depth, leftChild = None, rightChild = None):
        self.left = leftChild
        self.right = rightChild
        self.function = function
        self.depth = depth
        if isinstance(self.function, float) or isinstance(self.function, int) or self.function in leafFunctions:
            self.isLeaf = True
        else:
            self.isLeaf = False
            
	#get tree output recursively
    def toString(self):
        outString = ''
        for depthLevel in range(self.depth):
            outString += '|'
        outString += str(self.function)
        if self.function in nonLeafFunctions:
            outString += '\n' + self.left.toString() + '\n' + self.right.toString()
        return outString
        
	#get score recursively
    def getScore(self, sensorValues):
        try:
            self.function = float(self.function)
        except:
            a = 0
        if self.function in sensorValues:
            return sensorValues[self.function]
        if isinstance(self.function, float) or isinstance(self.function, int):
            return self.function
        if self.function == '+':
            return self.left.getScore(sensorValues) + self.right.getScore(sensorValues)
        if self.function == '-':
            return self.left.getScore(sensorValues) - self.right.getScore(sensorValues)
        if self.function == '*':
            return self.left.getScore(sensorValues) * self.right.getScore(sensorValues)
        if self.function == '/':
            r = self.right.getScore(sensorValues)
            if r == 0:
                return 10000
            else:
                return self.left.getScore(sensorValues) / r
        if self.function == 'RAND':
            return random.uniform(self.left.getScore(sensorValues), self.right.getScore(sensorValues))
        print("Invalid tree function: ", self.function)

    #Used for getting list of all nodes in tree to select one randomly
    def appendNode(self, nodes):
        nodes.append(self)
        if self.function in nonLeafFunctions:
            self.left.appendNode(nodes)
            self.right.appendNode(nodes)
    
#tree class	
class GPTree:
    def __init__(self, maxDepth, isFull):
        if isFull:
            self.root = makeFullTree(0, maxDepth)
        else:
            self.root = makeNotFullTree(0, maxDepth)
        self.fitness = 0
        self.runString = ''
        
	#evaluates tree for each move and picks the best one
    def chooseMove(self, moves):
        bestMove = max(moves, key = self.getScore)
        return bestMove
        
    def toString(self):
        return self.root.toString()
        
    def getScore(self, board):
        return self.root.getScore([])

    #Get all nodes for picking one randomly or counting them
    def getAllNodes(self):
        nodes = []
        self.root.appendNode(nodes)
        return nodes
        
    def pickChessMove(self, board, moves):
        moveScores = []
        for move in moves:
            board.push(move)
            sensorValues = getSensorValues(board)
            moveScores.append([self.root.getScore(sensorValues), move])
            board.pop()
        moveScores.sort(key=lambda x:x[0], reverse=True)
        return moveScores[0][1]
        
def lineToGPNode(lines):
    line = lines[0]
    lines.remove(line)
    depth = len(line) - len(line.replace('|', ''))
    line = line.replace('|', '')
    function = line
    if function in nonLeafFunctions:
        node = GPNode(function, depth, lineToGPNode(lines), lineToGPNode(lines))
        node.isLeaf == False
        return node
    else:
        node = GPNode(function, depth)
        node.isLeaf == True
        return node
        
def fileToGPTree(treeFile):
    treeText = open(treeFile)
    treeLines = treeText.readlines()
    for lineIndex in range(len(treeLines)):
        treeLines[lineIndex] = treeLines[lineIndex].replace('\n', '')
    root = lineToGPNode(treeLines)
    tree = GPTree(0, False)
    tree.root = root
    return tree

#makes random tree recursively (but not full)
def makeNotFullTree(depth, maxDepth):
    if depth < maxDepth:
        function = random.choice(functions)
        if function in nonLeafFunctions:
            childDepth = depth + 1
            node = GPNode(function, depth, makeNotFullTree(childDepth, maxDepth), makeNotFullTree(childDepth, maxDepth))
        else:
            if function == 'C':
                function = random.random() * 50
            node = GPNode(function, depth)
    else:
        function = random.choice(leafFunctions)
        if function == 'C':
            function = random.random() * 50
        node = GPNode(function, depth)
    return node
     
#makes random tree recursively
def makeFullTree(depth, maxDepth):
    if depth < maxDepth:
        function = random.choice(nonLeafFunctions)
        childDepth = depth + 1
        node = GPNode(function, depth, makeFullTree(childDepth, maxDepth), makeFullTree(childDepth, maxDepth))
    else:
        function = random.choice(leafFunctions)
        if function == 'C':
            function = random.random() * 50
        node = GPNode(function, depth)
    return node
    
#=============Survival selection stuff===========
#Get winner of a kTournament
def kTournament(population, k):
    #Get tournament entrants
    tournamentPopulation = random.sample(population, k)
    #Put them in descending order of penalized fitness
    tournamentPopulation.sort(key=lambda x:x.penalizedFitness, reverse=True)
    #Return first in group
    return tournamentPopulation[0]
    
def survivorKTournament(population, config):
    survivors = []
    for survivorNumber in range(config["numberOfParents"]):
        survivor = kTournament(population, config["survivorSelection"]["k"])
        survivors.append(survivor)
        population.remove(survivor)
    return survivors
    
#get survivors by trucation
def truncateSurvivors(population, numSurvivors):
    #sort by fitness descending and take the number we want
    population.sort(key=lambda x:x.penalizedFitness, reverse=True)
    return population[:numSurvivors]
    
#get survivors based on config
def getSurvivors(population, config):
    if config["survivorSelection"]["mode"] == "k":
        return survivorKTournament(population, config)
    if config["survivorSelection"]["mode"] == "t":
        return truncateSurvivors(population, config["numberOfParents"])
        
#============Child making stuff============
#copy tree because python copys by reference
def treeCopy(tree):
    newRoot = nodeCopy(tree.root, 0)
    newTree = GPTree(True, 0)
    newTree.root = newRoot
    return newTree

#copy node(along with it's children) because python copys by reference, but use new depth
def nodeCopy(node, depth):
    try:
        childDepth = depth + 1
        newNode = GPNode(node.function, depth, nodeCopy(node.left, childDepth), nodeCopy(node.right, childDepth))
    except:
        newNode = GPNode(node.function, depth)
    return newNode

#mutate tree
def getTreeMutation(tree):
    newTree = treeCopy(tree)
    node = random.choice(newTree.getAllNodes())
    newNode = makeNotFullTree(node.depth, node.depth + 3)
    node.function = newNode.function
    node.left = newNode.left
    node.right = newNode.right
    node.isLeaf = newNode.isLeaf
    return newTree

#replace a node in parent1 (and it's children) with a node in parent2 (and it's children) and return as new tree
def combineTrees(parent1, parent2):
    parent1Copy = treeCopy(parent1)
    parent1Node = random.choice(parent1Copy.getAllNodes())
    parent2Node = nodeCopy(random.choice(parent2.getAllNodes()), parent1Node.depth)
    parent1Node.function = parent2Node.function
    parent1Node.left = parent2Node.left
    parent1Node.right = parent2Node.right
    parent1Node.isLeaf = parent2Node.isLeaf
    return parent1Copy
    
#Create children using proportional selection
def proportionalParentSelection(parents):
    totalFitness = sum(parent.penalizedFitness for parent in parents)
    if totalFitness == 0:
        return random.choice(parents)
    #get random number in [0, totalFitness)
    rngNum = random.randrange(0, totalFitness)
    selectedParent = ""
    parentsChecked = 0
    #For every parent, add their fitness to parentsChecked, and if the parentsCheck is now bigger than rngNum, that is the parent.
    #This gives each parent their (parentFitness / totalFitness) chance to be picked
    for parent in parents:
        parentsChecked += parent.penalizedFitness
        if parentsChecked > rngNum:
            selectedParent = parent
            break
    
    #return the selected parent
    return selectedParent
   
#Gets a parent by over selection
def parentOverSelection(parents, cutoff):
    #80% of the time, select from the top bit
    if random.random() < .8:
        return random.choice(parents[:cutoff])
    else:
        return random.choice(parents[cutoff:])
    
#gets children from the current set of parents based on how the config says to
def selectParent(parents, config):
    if config["parentSelection"]["mode"] == "o":
        return parentOverSelection(parents, int(config["numberOfParents"] * float(config['parentSelection']['overSelectionCutoff'])))
    if config["parentSelection"]["mode"] == "p":
        return proportionalParentSelection(parents)
    
def getChild(parents, config):
    parent1 = selectParent(parents, config)
    #if random number < mutationChance, mutate just 1 parent
    if random.random() < float(config['mutationChance']):
        child = getTreeMutation(parent1)
        return child
    #else recombine 2 parents
    else:
        #make sure not to get parent1 twice
        parents.remove(parent1)
        parent2 = selectParent(parents, config)
        child = combineTrees(parent1, parent2)
        #put parent1 back
        parents.append(parent1)
        return child
        

def getChildren(parents, config):
    children = []
    for child in range(int(config['numberOfChildren'])):
        child = getChild(parents, config)
        children.append(child)
    return children
        
  
#===========General running stuff==========  
def randomMove(moves):
    return random.choice(moves)
       
def evaluation(tree, config):    
    fitness = 0
    chessPlayer = Player("custom", tree.pickChessMove)
    opponent = Player(config["opponent"])
    for i in range(5):
        gameEndBoard = play(chessPlayer, opponent)
        gameScore = 0
        pieces = gameEndBoard.piece_map()
        result = gameEndBoard.result()
        if result == '1-0':
            for piece in pieces:
                symbol = pieces[piece].symbol()
                if symbol in white_pieces:
                    gameScore += chess_piece_values[symbol]
            fitness += gameScore
        if result == '0-1':
            for piece in pieces:
                symbol = pieces[piece].symbol()
                if symbol in black_pieces:
                    gameScore += chess_piece_values[symbol]
            fitness += gameScore
    tree.fitness = fitness
    tree.penalizedFitness = tree.fitness - (float(config["penaltyCoefficient"]) * len(tree.getAllNodes()))
     
#determine whether or not it is time to terminate based on config
def terminateRun(generationsSinceImprovedBestFitness, numEvaluations, config):
    if config["terminationConditions"]["mode"] == "e":
        return numEvaluations >= int(config["terminationConditions"]["n"])
    if config["terminationConditions"]["mode"] == "b":
        return generationsSinceImprovedBestFitness >= int(config["terminationConditions"]["n"])
    
     
def run(configFile = "./configs/default.cfg"):
    configText = open(configFile).read()
    runLogText = "Result Log\n"
    runLogText += configText
    config = json.loads(configText)
    #If no random seed is given, use current time in microseconds
    if config["randomSeed"] == "":
        config["randomSeed"] = int(time.time() * 1000000)
        runLogText += "\nTime in microseconds: " + str(config["randomSeed"])
    else:
        config["randomSeed"] = int(config["randomSeed"])
    random.seed(config["randomSeed"])
    
    bestFitnessEver = -10000
    bestEverWorldString = ""
    bestEverTreeString = ""
    
    for run in range(1, int(config["runs"]) + 1):
        runLogText += "\n\nRun " + str(run)
        numEvaluations = 0  
        bestFitnessRun = -10000
        print("Run: ", run)
        
        #Get parents using ramped half and half
        parents = []
        for fullParent in range(int(config["numberOfParents"]) // 2):
            tree = GPTree(config["maxTreeDepth"], True)
            parents.append(tree)
        for notFullParent in range(int(config["numberOfParents"]) // 2, int(config["numberOfParents"])):
            tree = GPTree(config["maxTreeDepth"], False)
            parents.append(tree)
            
        #Evaluate the parents
        for parent in parents:
            evaluation(parent, config)
            numEvaluations += 1
            
			#If best fitness ever, make it the best world and solution files
            if parent.fitness > bestFitnessEver:
                bestFitnessEver = parent.fitness
                bestEverWorldString = parent.runString
                bestEverTreeString = parent.toString()
                
        generationsSinceImprovedBestFitness = 0
            
        while not(terminateRun(generationsSinceImprovedBestFitness, numEvaluations, config)):
            generationsSinceImprovedBestFitness += 1
            children = getChildren(parents, config)
            #Evaluate the children
            for child in children:
                evaluation(child, config)
                numEvaluations += 1
                    
            parents.extend(children)
            avgFitnessGeneration = float(sum(parent.fitness for parent in parents)) / float(len(parents))
            parents.sort(key=lambda x:x.fitness, reverse=True)
            bestFitnessGeneration = parents[0].fitness
            
            if parents[0].fitness > bestFitnessRun:
                bestFitnessRun = parents[0].fitness
                generationsSinceImprovedBestFitness = 0
                
            #If best fitness ever, make it the best world and solution files
            if parents[0].fitness > bestFitnessEver:
                bestFitnessEver = parents[0].fitness
                bestEverTreeString = parents[0].toString()
                
            runLogText += "\n" + str(numEvaluations) + "\t" + str(avgFitnessGeneration) + "\t" + str(bestFitnessGeneration)
            print(numEvaluations, avgFitnessGeneration, bestFitnessGeneration)
            
            parents = getSurvivors(parents, config)
            
            
                    
    
    logFile = open(config["logFilePath"], 'w')
    logFile.write(runLogText)
    solutionFile = open(config["solutionFilePath"], 'w')
    solutionFile.write(bestEverTreeString)
    print("Done")
    
        
    
def main():
    if len(sys.argv) > 1:
        run(sys.argv[1])
    else:
        #cProfile.run('run()')
        run()  
       
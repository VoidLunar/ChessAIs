#### SELF PLAY
EPISODES = 25
MCTS_SIMS = 1
MEMORY_SIZE = 2000
TURNS_UNTIL_TAU0 = 30 # turn on which it starts playing deterministically
CPUCT = 1
EPSILON = 0.2
ALPHA = 0.9


#### RETRAINING
BATCH_SIZE = 256
EPOCHS = 1
REG_CONST = 0.0001
LEARNING_RATE = 0.1
MOMENTUM = 0.9
TRAINING_LOOPS = 5

HIDDEN_CNN_LAYERS = [
	{'filters': 16, 'kernel_size': (4, 4)}
	, {'filters': 16, 'kernel_size': (4, 4)}
	, {'filters': 16, 'kernel_size': (4, 4)}
	, {'filters': 16, 'kernel_size': (4, 4)}
	, {'filters': 16, 'kernel_size': (4, 4)}
	, {'filters': 16, 'kernel_size': (4, 4)}
	, {'filters': 16, 'kernel_size': (4, 4)}
	, {'filters': 16, 'kernel_size': (4, 4)}
	, {'filters': 16, 'kernel_size': (4, 4)}
	, {'filters': 16, 'kernel_size': (4, 4)}
	, {'filters': 16, 'kernel_size': (4, 4)}
	, {'filters': 16, 'kernel_size': (4, 4)}
]

#### EVALUATION
EVAL_EPISODES = 20
SCORING_THRESHOLD = 1.2
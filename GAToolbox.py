import random
import math
import operator
from deap import creator, base, tools, gp
from FilterSet import filters
from protectedDiv import protectedDiv

def evalSymbReg(individual, points, toolbox):
	# Transform the tree expression in a callable function
	func = toolbox.compile(expr=individual)
	# Evaluate the mean squared error between the expression
	# and the function to analyse
	sqerrors = ((func(x) - individual.target_func(x))**2 for x in points)
	return math.fsum(sqerrors) / len(points),

def get_toolbox(target_func):

	# collect the atomic building blocks of the individuals
	pset = gp.PrimitiveSet("MAIN", 1)
	pset.addPrimitive(operator.add, 2)
	pset.addPrimitive(operator.sub, 2)
	pset.addPrimitive(operator.mul, 2)
	pset.addPrimitive(protectedDiv, 2)
	pset.addPrimitive(operator.neg, 1)
	pset.addPrimitive(math.cos, 1)
	pset.addPrimitive(math.sin, 1)
	pset.addEphemeralConstant("rand101", lambda: random.randint(-1,1))
	pset.addEphemeralConstant("rand10010", lambda: random.randint(-10,10))
	pset.addTerminal(math.pi)

	# define the general form of an individual
	creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
	creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin, target_func=target_func)

	toolbox = base.Toolbox()

	toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=3)
	toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
	toolbox.register("population", tools.initRepeat, list, toolbox.individual)
	toolbox.register("compile", gp.compile, pset=pset)

	eval_range = [x/10. for x in range(-10,10)] + [x for x in range(-100, 100)]
	toolbox.register("evaluate", evalSymbReg, points=eval_range, toolbox=toolbox)
	
	# add filters for unwanted behaviour
	for filter_ in filters:
		toolbox.decorate('evaluate', tools.DeltaPenalty(filter_, 1000.))
	
	toolbox.register("select", tools.selTournament, tournsize=3)
	toolbox.register("mate", gp.cxOnePoint)
	toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
	toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

	toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
	toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
	return toolbox

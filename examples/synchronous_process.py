import matplotlib.pyplot as plt
import numpy as np

import peal

A = np.array([4, 74, 43, 23, 0])

pool = peal.genetics.IntegerPool(shape=A.size, lower=0, upper=101)


@peal.fitness
def evaluate(individual: peal.Individual) -> float:
    """Negative MSE comparing individuals genes to A."""
    return -np.mean((A - individual.genes)**2)


strategy = peal.core.Strategy(
    init_individuals=100,
    generations=100,
    selection=peal.operators.selection.Tournament(size=4),
    mutation=peal.operators.mutation.UniformInt(
        prob=0.1,
        lowest=0,
        highest=100,
    ),
    reproduction=peal.operators.reproduction.Crossover(
        npoints=1,
        probability=0.7,
    ),
    integration=peal.operators.integration.Crowded(10),
)

environment = peal.core.Environment(
    pool=pool,
    fitness=evaluate,
)

tracker = peal.callback.BestWorst()
statistics = peal.callback.Diversity(pool=pool)

environment.execute(strategy, callbacks=[tracker, statistics])

print(tracker.best)

# - plotting -

fig = plt.figure(figsize=(10, 5))

axis1 = fig.add_subplot(2, 1, 1)
axis1.plot(tracker.best.fitness)
axis1.set_title("Fitness")

axis2 = fig.add_subplot(2, 1, 2)
axis2.plot(statistics.diversity)
axis2.set_title("Diversity")

plt.show()

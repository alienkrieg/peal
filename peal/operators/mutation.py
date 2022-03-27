"""Module that defines operators that mutate individuals or populations.
"""

from typing import Optional
import numpy as np

from peal.operators.operator import Operator
from peal.population import Population


class BitFlip(Operator):
    """Mutation that applies the python ``not`` operator to genes in
    an individual.

    Args:
        prob (float, optional): The probability of each gene to mutate.
            Defaults to 0.1.
    """

    def __init__(self, prob: float = 0.1) -> None:
        super().__init__()
        self._prob = prob

    def _process_population(
        self,
        container: Population,
    ) -> Population:
        ind = container[0].copy()
        for i, gene in enumerate(ind.genes):
            if np.random.random_sample() <= self._prob:
                ind.genes[i] = not gene
        return Population(ind)


class UniformInt(Operator):
    """Mutation that selects a random uniformly distributed integer from
    a given range with a certain probability for a single gene.

    Args:
        prob (float, optional): The probability of each gene to mutate.
            Defaults to 0.1.
        lowest (int, optional): The lowest integer the mutation can turn
            a gene to. Defaults to -1.
        highest (int, optional): The highest integer the mutation can
            turn a gene to. Defaults to 1.
    """

    def __init__(
        self,
        prob: float = 0.1,
        lowest: int = -1,
        highest: int = 1,
    ) -> None:
        super().__init__()
        self._prob = prob
        self._lowest = lowest
        self._highest = highest

    def _process_population(
        self,
        container: Population,
    ) -> Population:
        ind = container[0].copy()
        hits = np.where(
            np.random.random_sample(len(ind.genes)) <= self._prob
        )[0]
        ind.genes[hits] = np.random.randint(
            self._lowest,
            self._highest+1,
            size=len(hits),
        )
        return Population(ind)


class UniformFloat(Operator):
    """Mutation that mutates a gene to a random float in a given range
    with certain probability.

    Args:
        prob (float, optional): The probability of each gene to mutate.
            Defaults to 0.1.
        lowest (float, optional): The lowest float the mutation can turn
            a gene to. Defaults to -1.
        highest (float, optional): The highest float the mutation can
            turn a gene to. Defaults to 1.
    """

    def __init__(
        self,
        prob: float = 0.1,
        lowest: float = -1.0,
        highest: float = 1.0,
    ) -> None:
        super().__init__()
        self._prob = prob
        self._lowest = lowest
        self._highest = highest

    def _process_population(
        self,
        container: Population,
    ) -> Population:
        ind = container[0].copy()
        hits = np.where(
            np.random.random_sample(len(ind.genes)) <= self._prob
        )[0]
        ind.genes[hits] = (
            (self._highest-self._lowest)
            * np.random.random_sample(size=len(hits))
            + self._lowest
        )
        return Population(ind)


class NormalDist(Operator):
    """Mutation operator that changes genes for an individual with a
    probability by __adding__ a randomly distributed real value.

    Args:
        prob (float, optional): The probability of each gene to mutate.
            Defaults to 0.1.
        mu (float, optional): The mean of the normal distribution the
            values are drawn from. Defaults to 0.
        sigma (float, optional): The standard deviation of the normal
            distribution the values are drawn from. Defaults to 1.
        alpha (float, optional): If a float value is given, the
            mutation step size (i.e. the standard deviation of a
            normal distribution) will be multiplied by this float or its
            inverse (randomly chosen) each time an individual is passed
            through this operator. Each individual then has its own
            mutation step size saved in their object representation as
            hidden parameters. Defaults to None.
    """

    def __init__(
        self,
        prob: float = 0.1,
        mu: float = 0.0,
        sigma: float = 1.0,
        alpha: Optional[float] = None,
    ) -> None:
        super().__init__()
        self._prob = prob
        self._mu = mu
        self._sigma = sigma
        self._alpha = alpha

    def _process_population(
        self,
        container: Population,
    ) -> Population:
        ind = container[0].copy()
        hits = np.where(
            np.random.random_sample(len(ind.genes)) <= self._prob
        )[0]
        sigma = self._sigma
        if self._alpha is not None:
            sigma = ind.hidden_genes[0]
            ind.hidden_genes[0] *= np.random.choice(
                [self._alpha, 1/self._alpha]
            )
        ind.genes[hits] += np.random.normal(
            self._mu,
            sigma,
            size=len(hits),
        )
        return Population(ind)

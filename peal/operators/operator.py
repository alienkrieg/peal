"""Module that provides the base operator class."""

from typing import Optional, Union, overload
import warnings

import numpy as np

from peal.community import Community
from peal.genetics import GenePool
from peal.operators.iteration import IterationType, SingleIteration
from peal.population import Population


class Operator:
    """Base class for evolutionary operators in peal. An operator is
    normally called on a :class:`~peal.population.Population` or a
    :class:`~peal.community.Community`. Smaller parts of such a
    container are selected by ``iter_type`` and fed forward to the
    protected methods :meth:`Operator._process_population` or
    :meth:`Operator._process_community` that can be overwritten by
    inheriting classes. By default, they do not change the given object.

    Args:
        iter_type (IterationType, optional): The iteration type of the
            operator. This property is used to iterate over the input
            population or community, and yields corresponding smaller
            populations or communities, which then are given to the
            protected methods. All results will be concatenated and
            returned by the public :meth:`Operator.process` method.
            Defaults to
            :class:`peal.operations.iteration.SingleIteration`
    """

    def __init__(
        self,
        iter_type: Optional[IterationType] = None,
    ) -> None:
        self._iter_type = SingleIteration() if iter_type is None else iter_type

    @property
    def iter_type(self) -> IterationType:
        """The type of iteration through a population to use if the
        operators :meth:`process` method is called on a population. This
        leads to the processing of single individuals in the population.
        In which order they are processed or how many individuals are
        processed at once will be specified by such an iteration type.
        """
        return self._iter_type

    @iter_type.setter
    def iter_type(self, iter_type: IterationType) -> None:
        if not isinstance(iter_type, IterationType):
            raise TypeError(f"Expected IterationType, got {type(iter_type)}")
        self._iter_type = iter_type

    @overload
    def process(
        self,
        container: Population,
        /, *,
        pool: Optional[GenePool] = None,
    ) -> Population:
        ...

    @overload
    def process(
        self,
        container: Community,
        /, *,
        pool: Optional[GenePool] = None,
    ) -> Community:
        ...

    def process(
        self,
        container: Union[Population, Community],
        /, *,
        pool: Optional[GenePool] = None,
    ) -> Union[Population, Community]:
        """Processes and returns the given population or community."""
        if isinstance(container, Population):
            population = Population()
            for batch in self._iter_type(container):
                population.integrate(
                    self._process_population(batch, pool=pool)
                )
            return population
        if isinstance(container, Community):
            community = Community()
            for population_batch in self._iter_type(container):
                community.integrate(
                    self._process_community(population_batch, pool=pool)
                )
            return community
        raise TypeError("Operator can only process populations or communities")

    def _process_population(
        self,
        container: Population,
        /, *,
        pool: Optional[GenePool] = None,
    ) -> Population:
        warnings.warn(
            f"Operator {type(self).__name__} has been called on a"
            "Population without specifying an operation for this "
            "type of container; it will not be processed",
            category=UserWarning,
        )
        return container

    def _process_community(
        self,
        container: Community,
        /, *,
        pool: Optional[GenePool] = None,
    ) -> Community:
        warnings.warn(
            f"Operator {type(self).__name__} has been called on a"
            "Community without specifying an operation for this "
            "type of container; it will not be processed",
            category=UserWarning,
        )
        return container

    def __repr__(self) -> str:
        return self.__class__.__name__


class OperatorChain:
    """Class that chains :class:`~peal.operators.operator.Operator`
    objects together.
    The method :meth:`OperatorChain.process` processes the given
    Population or Community with every operator in the order they are
    given.

    Args:
        operators (Operator | list[Operator]): Any number of operators
            or lists of operators. If a list is given, the operator will
            be randomly selected from that list before processing the
            given container.
    """

    def __init__(self, *operators: Union[Operator, list[Operator]]) -> None:
        self._operators = operators

    @overload
    def process(
        self,
        container: Population,
        /, *,
        pool: Optional[GenePool] = None,
    ) -> Population:
        ...

    @overload
    def process(
        self,
        container: Community,
        /, *,
        pool: Optional[GenePool] = None,
    ) -> Community:
        ...

    def process(
        self,
        container: Union[Population, Community],
        /, *,
        pool: Optional[GenePool] = None,
    ) -> Union[Population, Community]:
        """Processes and returns the given population or community."""
        for operator in self._operators:
            if isinstance(operator, list):
                operator = operator[np.random.randint(len(operator))]
            container = operator.process(container, pool=pool)
        return container

    def __repr__(self) -> str:
        return " - ".join([
            f"({' | '.join(map(str, x))})" if isinstance(x, list) else str(x)
            for x in self._operators
        ])

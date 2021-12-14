from itertools import chain
from typing import Dict

from microcosm_fastapi.conventions.build_info.models import BuildInfo
from microcosm_fastapi.conventions.health.resources import HealthResultSchema, HealthSchema
from microcosm_fastapi.errors import ParsedException


class HealthResult:
    def __init__(self, error=None, result=None):
        self.error = error
        self.result = result or "ok"

    def __nonzero__(self):
        return self.error is None

    def __bool__(self):
        return self.error is None

    def __str__(self):
        return self.result if self.error is None else self.error

    def to_object(self):
        return HealthResultSchema(
            ok=bool(self),
            message=str(self),
        )

    @classmethod
    def evaluate(cls, func, graph) -> "HealthResult":
        try:
            result = func(graph)
            return cls(result=result)
        except Exception as error:
            parsed_exception = ParsedException(error)
            return cls(error=parsed_exception.error_message)


class Health:
    """
    Wrapper around service health state.
    May contain zero or more "checks" which are just callables that take the
    current object graph as input.
    The overall health is OK if all checks are OK.
    """

    def __init__(self, graph, include_build_info=True):
        self.graph = graph
        self.name = graph.metadata.name
        self.optional_checks = dict()
        self.checks = dict()

        if include_build_info:
            self.checks.update(
                dict(
                    build_num=BuildInfo.check_build_num,
                    sha1=BuildInfo.check_sha1,
                )
            )

    def to_object(self, full=None) -> HealthSchema:
        """
        Encode the name, the status of all checks, and the current overall status.
        """
        if full:
            checks = chain(self.checks.items(), self.optional_checks.items())
        else:
            checks = self.checks.items()

        # evaluate checks
        check_results: Dict[str, HealthResult] = {
            key: HealthResult.evaluate(func, self.graph)
            for key, func in checks
        }

        health = HealthSchema(
            # return the service name helps for routing debugging
            name=self.name,
            ok=all(check_results.values()),
        )

        if checks:
            health.checks = {
                key: check_results[key].to_object()
                for key in sorted(check_results.keys())
            }

        return health

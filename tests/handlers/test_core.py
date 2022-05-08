import pytest

from mona.core import ContextError, HTTPContext
from mona.handlers.core import choose, error_handler, http_handler
from mona.monads.future import Future


def test_http_handler(ctx: HTTPContext):
    assert ctx >> http_handler(lambda x: x) == ctx
    assert isinstance(ContextError(ctx) >> http_handler(lambda _: ctx), ContextError)


def test_error_handler(ctx: HTTPContext):
    assert ctx >> error_handler(lambda x: None) == ctx
    assert ContextError(ctx) >> error_handler(lambda x: ctx) == ctx


@http_handler
def sync_success_handler(ctx: HTTPContext) -> HTTPContext:
    return ctx


@http_handler
async def async_success_handler(ctx: HTTPContext) -> HTTPContext:
    return ctx


@http_handler
def fail_handler(ctx: HTTPContext) -> ContextError:
    return ContextError(ctx)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "funcs, result_type",
    [
        ([], HTTPContext),
        # ([fail_handler], HTTPContext),
        # ([sync_success_handler], HTTPContext),
        ([async_success_handler], HTTPContext),
        # ([fail_handler, sync_success_handler], HTTPContext),
        # ([sync_success_handler, fail_handler], HTTPContext),
        # ([sync_success_handler, async_success_handler], HTTPContext),
        # ([sync_success_handler, sync_success_handler], HTTPContext),
        ([async_success_handler, async_success_handler], HTTPContext),
        # ([async_success_handler, sync_success_handler], HTTPContext),
    ],
)
async def test_choose(ctx: HTTPContext, funcs, result_type):
    assert isinstance(
        await (Future.create(ctx) >> choose(*funcs)),
        result_type,
    )

from __future__ import annotations

import pytest
from contextlib import ExitStack
import anyio

from aiomqtt.topic import Topic, Wildcard, SubscriptionTree, Subscription
from aiomqtt.message import Message


def test_sub_dispatch() -> None:
    """Test that Topic raises Exceptions for invalid topics."""
    tree = SubscriptionTree()
    a = Subscription("a/#")
    b = Subscription("a/b/#")
    c = Subscription("a/b/c")
    d = Subscription("a/b/c/d")

    subs = (a,b,c,d)
    with ExitStack() as e:
        for sb in subs:
            e.enter_context(sb.subscribed_to(tree))

        def chk(topic, ok):
            m = Message(topic, 123, 0, False,321,{})
            tree.dispatch(m)

            for sb in subs:
                try:
                    msg = sb.queue.get_nowait()
                except anyio.WouldBlock:
                    assert sb not in ok, (topic,sb.topic)
                else:
                    assert msg is m
                    assert sb in ok, (topic,sb.topic)

        chk("x", ())
        chk("a", (a,))
        chk("a/x/y", (a,))
        chk("a/b", (a,b))
        chk("a/b/x", (a,b))
        chk("a/b/c", (a,b,c))
        chk("a/b/c/d", (a,b,d))
        chk("a/b/c/d/e", (a,b))

    chk("a/x/y", ())

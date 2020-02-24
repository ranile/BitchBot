import asyncio
import functools
import json
import pprint
import datetime
import pendulum
import dateparser

settings = {
    'TIMEZONE': 'UTC',
    'RETURN_AS_TIMEZONE_AWARE': True,
    'TO_TIMEZONE': 'UTC',
    'PREFER_DATES_FROM': 'future'
}

inp = "1h this is a user"

times = []
loop = asyncio.get_event_loop()


async def parse(user_input):
    to_be_passed = f"in {user_input}"
    split = to_be_passed.split(" ")
    length = len(split[:7])
    out = None
    used = ""
    start = datetime.datetime.utcnow()
    while out is None:
        used = " ".join(split[:length])
        s = datetime.datetime.utcnow()
        fut = loop.run_in_executor(None, functools.partial(dateparser.parse, used, settings=settings))
        print(type(fut))
        try:
            out = await asyncio.wait_for(fut, 1.0)
        except asyncio.TimeoutError:
            fut.cancel()

        e = datetime.datetime.utcnow()
        print(e-s, used)
        times.append(e-s)
        length -= 1

    now = datetime.datetime.utcnow()
    p_time = pendulum.instance(out.replace(tzinfo=now.tzinfo))
    p_now = pendulum.instance(now)
    return {
        'time': p_time,
        'string': to_be_passed,
        'now': p_now,
        'other': "".join(to_be_passed).replace(used, ""),
        'time_took': (now-start).total_seconds()
    }


async def main():
    parsed = await parse(inp)
    print(pprint.pformat(parsed))
    print(times)

loop.run_until_complete(main())

import asyncio
from engine import SeleniumMapsEngine

def safe_print(msg):
    with open('test_log.txt', 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

async def test():
    engine = SeleniumMapsEngine("electricians in london", 5, True, log_callback=safe_print)
    try:
        async for i, t, l in engine.run_generator():
            pass
    except Exception as e:
        import traceback
        safe_print(f"ERROR: {e}\n{traceback.format_exc()}")

asyncio.run(test())

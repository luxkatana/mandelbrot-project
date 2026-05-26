import websockets, asyncio, json
import rich

MASTER = ("127.0.0.1", 8000)


async def main():
    async with websockets.connect(f"ws://{MASTER[0]}:{MASTER[1]}/attend") as wsclient:
        payloaddata = await wsclient.recv()
        payloaddata = json.loads(payloaddata)
        rich.print(payloaddata)


if __name__ == "__main__":
    asyncio.run(main())

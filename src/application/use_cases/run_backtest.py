import asyncio
from concurrent.futures import ProcessPoolExecutor
from src.domain.strategies import run_monte_carlo_simulation


class RunBacktestUseCase:
    def __init__(self, pool: ProcessPoolExecutor):
        self.pool = pool

    async def execute(self, price: float, iterations: int = 5_000_000) -> dict:
        """
        Offloads the calculation to a separate process.
        The Main Event Loop remains FREE to handle other API requests.
        """
        loop = asyncio.get_running_loop()

        # run_in_executor(Executor, Function, *Args)
        result = await loop.run_in_executor(
            self.pool,
            run_monte_carlo_simulation,
            price,
            iterations
        )

        return result
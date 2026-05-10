import asyncio
import logging
from typing import Any, Set

logger = logging.getLogger("rpa-bridge")


class BackgroundTaskRegistry:
    """
    Maintains strong references to in-flight asynchronous tasks to prevent
    premature garbage collection and ensures graceful shutdown.
    """

    def __init__(self) -> None:
        # Set maintains strong references to active tasks
        self.tasks: Set[asyncio.Task[Any]] = set()

    def add(self, task: asyncio.Task[Any]) -> None:
        """Registers a task and automatically removes it upon completion."""
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)

    async def wait_all(self, timeout: float = 25.0) -> None:
        """Awaits completion of all tasks, forcibly cancelling any that exceed the timeout."""
        if not self.tasks:
            return

        logger.info(
            f"Graceful shutdown: Awaiting {len(self.tasks)} in-flight background task(s)..."
        )

        _, pending = await asyncio.wait(self.tasks, timeout=timeout)

        if pending:
            logger.warning(
                f"Shutdown timeout ({timeout}s) reached. Forcibly cancelling {len(pending)} hanging task(s)."
            )

            # 1. Issue the kill signal to all hanging tasks
            for task in pending:
                task.cancel()

            # 2. Allow the event loop a brief moment to process the cancellations
            await asyncio.gather(*pending, return_exceptions=True)
        else:
            logger.info(
                "All background tasks completed successfully prior to shutdown."
            )


task_registry = BackgroundTaskRegistry()

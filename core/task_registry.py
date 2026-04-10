import asyncio
import logging

logger = logging.getLogger("rpa-bridge")


class BackgroundTaskRegistry:
    def __init__(self):
        self.tasks = set()

    def add(self, task: asyncio.Task) -> None:
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)

    async def wait_all(self, timeout: float = 25.0) -> None:
        if self.tasks:
            logger.info(
                f"Graceful shutdown: Waiting for {len(self.tasks)} in-flight background tasks..."
            )
            done, pending = await asyncio.wait(self.tasks, timeout=timeout)
            if pending:
                logger.warning(
                    f"Shutdown timeout reached. {len(pending)} tasks forcefully terminated."
                )
            else:
                logger.info("All background tasks completed successfully.")


task_registry = BackgroundTaskRegistry()

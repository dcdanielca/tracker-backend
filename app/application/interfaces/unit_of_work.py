from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    """Interface del patrón Unit of Work"""

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        """Inicia una transacción"""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Finaliza la transacción (commit o rollback)"""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Confirma los cambios"""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Deshace los cambios"""
        pass

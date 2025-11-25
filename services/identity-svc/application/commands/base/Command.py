"""
Base classes for Command pattern
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from dataclasses import dataclass

TCommand = TypeVar('TCommand')
TResult = TypeVar('TResult')


@dataclass
class Command(ABC):
    """Base class for all commands"""
    pass


class CommandHandler(ABC, Generic[TCommand, TResult]):
    """Base class for command handlers"""
    
    @abstractmethod
    async def handle(self, command: TCommand) -> TResult:
        """Handle the command and return result"""
        pass
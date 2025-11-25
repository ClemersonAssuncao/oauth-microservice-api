"""
Command Bus for dispatching commands to handlers
"""
from typing import Dict, Type, TypeVar
from application.commands.base.Command import Command, CommandHandler

TCommand = TypeVar('TCommand', bound=Command)
TResult = TypeVar('TResult')


class CommandBus:
    """Central bus for dispatching commands to their handlers"""
    
    def __init__(self):
        self._handlers: Dict[Type[Command], CommandHandler] = {}
    
    def register(self, command_type: Type[TCommand], handler: CommandHandler[TCommand, TResult]):
        """Register a command handler"""
        self._handlers[command_type] = handler
    
    async def dispatch(self, command: TCommand) -> TResult:
        """Dispatch a command to its handler"""
        command_type = type(command)
        
        if command_type not in self._handlers:
            raise ValueError(f"No handler registered for command type: {command_type.__name__}")
        
        handler = self._handlers[command_type]
        return await handler.handle(command)
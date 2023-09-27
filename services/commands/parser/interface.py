import abc
from typing import TypeVar

from enums import CommandTypeEnum
from services.commands.dto import (
    CommandAddData,
    CommandDeleteAllData,
    CommandDeleteData,
    CommandMyData,
    CommandPriceData,
    CommandStepData,
)

T = TypeVar("T")


class CommandParserService(abc.ABC):
    def get_command_data(self, cmd: str) -> CommandAddData | CommandStepData | CommandDeleteData | CommandPriceData:
        command_type, data = self._get_command_type(cmd)
        match command_type:
            case CommandTypeEnum.ADD:
                callable_func = self._get_command_add_data
            case CommandTypeEnum.STEP:
                callable_func = self._get_command_step_data
            case CommandTypeEnum.PRICE:
                callable_func = self._get_command_price_data
            case CommandTypeEnum.DELETE:
                callable_func = self._get_command_delete_data
            case CommandTypeEnum.DELETE_ALL:
                callable_func = self._get_command_delete_all_data
            case CommandTypeEnum.MY:
                callable_func = self._get_command_my_data
            case _:
                raise ValueError
        return callable_func(data)

    @abc.abstractmethod
    def _get_command_type(self, cmd: str) -> tuple[CommandTypeEnum, T]:
        pass

    @abc.abstractmethod
    def _get_command_add_data(self, data: T) -> CommandAddData:
        pass

    @abc.abstractmethod
    def _get_command_step_data(self, data: T) -> CommandStepData:
        pass

    @abc.abstractmethod
    def _get_command_delete_data(self, data: T) -> CommandDeleteData:
        pass

    @abc.abstractmethod
    def _get_command_price_data(self, data: T) -> CommandPriceData:
        pass

    @abc.abstractmethod
    def _get_command_delete_all_data(self, data: T) -> CommandDeleteAllData:
        pass

    @abc.abstractmethod
    def _get_command_my_data(self, data: T) -> CommandMyData:
        pass

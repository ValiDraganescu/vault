from collections.abc import Callable
from enum import Enum

class Events(Enum):
    ADD_SECRET = "add_secret"
    FILE_SELECTED = "file_selected"
    UPDATE_SIDEBAR = "update_sidebar"


class EventBus(object):

    listeners = {}

    def subscribe(self, event, listener: callable):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(listener)

    def unsubscribe(self, event, listener: callable):
        if event in self.listeners:
            self.listeners[event].remove(listener)

    def emit(self, event, *args, **kwargs):
        if event in self.listeners:
            for listener in self.listeners[event]:
                listener(*args, **kwargs)
                

event_bus = EventBus()
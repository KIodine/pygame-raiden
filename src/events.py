import functools

class Event():

    def __init__(
            self,
            event,
            time
        ):
        self.event = event
        self.time = time
        self.maxtime = time
        self.is_ready = False

    def update(self):
        if self.time <= 0:
            self.is_ready = True
        return

class EventHandler():

    def __init__(
            self,
            clock
        ):
        self.clock = clock
        self.todos = list()

    def timed_event(
            self,
            func,
            time,
            *args,
            **kwargs
        ):
        thing = functools.partial(
            func, *args, **kwargs
        )
        event = Event(thing, time)
        self.todos.append(event)
        return

    def cycled_event(
            self
        ):
        # Do thing per n seconds.
        return

    def conditional_event(
            self
        ):
        # Do thing is condition is satisfied.
        return

    def update(self):
        elapsed = self.clock.get_time()
        for thing in self.todos:
            thing.time -= elapsed
            thing.update()
            if thing.is_ready:
                thing.event()
                self.todos.remove(thing)
        return

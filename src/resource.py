from functools import partial

class Resource():
    '''Resource container and manager.'''
    # Fixed data structure.
    __slots__ = [
        'name',
        'current_val',
        'max_val',
        'charge_val',
        'charge_speed',
        'last_charge',
        'delay',
        'delay_time',
        'last_val'
        ]

    def __init__(
            self,
            *,
            name='NONE',
            init_val=100,
            max_val=100,
            charge_val=1,
            charge_speed=0.1,
            init_time=0,
            delay=False,
            delay_time=1
        ):
        if max_val == 0:
            raise ValueError("Cannot set max_val as zero.")
        self.name = name
        self.current_val = init_val
        self.max_val = max_val
        self.charge_val = charge_val
        self.charge_speed = charge_speed
        self.last_charge = init_time # Replace with 'now'.

        self.delay = delay
        self.delay_time = delay_time
        self.last_val = init_val

    def __repr__(self):
        s = "<{name}: {current_val}/{max_val} ({ratio:.1f}%)>"
        return s.format(
            name=self.name,
            max_val=int(self.max_val),
            current_val=int(self.current_val),
            ratio=self.ratio*100
            )

    def recover(self, current_time):
        '''Recover resource over time.'''
        # The main method.
        def is_available():
            """Check a resource is ready to recover."""
            permission = False
            # Short-circuit, if 'delay' is 'False', it won't eval the rear code.
            if self.delay and self.last_val != self.current_val:
                self.last_charge = current_time
                # Reset last charge time(this is important).
                self.last_charge += self.delay_time * 1000
                self.last_val = self.current_val

            elapsed_time = current_time - self.last_charge
            if elapsed_time > self.charge_speed * 1000\
               and self.current_val < self.max_val:
                permission = True
            return permission

        if is_available():
            self.last_charge = current_time
            self.current_val += self.charge_val
            self._over_charge_check()
            self.last_val = self.current_val
        # Limit the minimum val to zero.
        if self.current_val < 0: self.current_val = 0
        return

    def charge(self, val=0):
        '''Charge resource with 'val'.'''
        if self.ratio < 1:
            self.current_val += val
            self._over_charge_check()
        return

    @property
    def ratio(self):
        c_val = self.current_val
        if c_val < 0: c_val = 0
        return c_val/self.max_val

    def _to_zero(self):
        '''Reduce resource to zero.'''
        self.current_val = 0
        return

    def _to_max(self):
        '''Charge resource to its maximum value.'''
        self.current_val = self.max_val
        return

    def _over_charge_check(self):
        '''If current_val exceeds max_val, set it to max_val.'''
        if self.current_val > self.max_val:
            self.current_val = self.max_val
        return

default_player_hp = partial(
    Resource,
    name='Health',
    init_val=100,
    max_val=100,
    charge_val=0.6,
    charge_speed=0.02,
    delay=True,
    delay_time=2
)

default_player_charge = partial(
    Resource,
    name='Charge',
    init_val=0,
    max_val=1000,
    charge_val=12,
    charge_speed=0.06
)

default_player_ultimate = partial(
    Resource,
    name='Ultimate',
    init_val=0,
    max_val=2000,
    charge_val=3,
    charge_speed=0.1,
    delay=True,
    delay_time=1
)

default_enemy_hp = partial(
    Resource,
    name='Health',
    init_val=100,
    max_val=100,
    charge_val=0,
)

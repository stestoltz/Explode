import sys


class ImmutableTape(str):
    def __getitem__(self, index):
        index %= len(self)
        return super().__getitem__(index)


class Tape(list):
    def __init__(self, tape_):
        list.__init__(self, tape_)

    def __getitem__(self, index):
        index %= len(self)
        return super().__getitem__(index)

    def __setitem__(self, index, item):
        index %= len(self)
        return super().__setitem__(index, item)

    """def insert(self, index, item, origin=None):
        for explorer_ in explorers:
            if (not origin or origin is not explorer_) and explorer_.index >= index:
                explorer_.index += 1

        super().insert(index, item)"""

    def insert(self, index, item):
        for explorer_ in explorers:
            if explorer_.index_ >= index:
                explorer_.index_ += 1

        super().insert(index, item)

BOMB = "BOMB"
EOL = "EOL"
NONE = " "

TYPE = "TYPE"
MODIFY = "&"
EXTEND = "%"
WRITE = "="
OVERWRITE = "*"
INSERT = "@"
TYPES = (MODIFY, EXTEND, WRITE, OVERWRITE, INSERT)

DIRECTION = "DIRECTION"
UP = "^"
DOWN = "_"
BOTH = "|"
DIRECTIONS = (UP, DOWN, BOTH)

ACTION = "ACTION"
ADD = "+"
SUBTRACT = "-"
WAVE = "~"
INCREASING = "/"
DECREASING = "\\"
ACTIONS = (ADD, SUBTRACT, WAVE, INCREASING, DECREASING)

SOURCE = "SOURCE"
INPUT = "?"
SOURCES = (INPUT,)

QUEUE = "QUEUE"
PUSH = "<"
WAIT = ">"
LAST = "!"
QUEUES = (PUSH, WAIT, LAST)


class Token:
    def __init__(self, type_, val):
        self.type = type_
        self.val = val

    def __repr__(self):
        return "Token('{}','{}')".format(self.type, self.val)


class Liner:
    def __init__(self, line):
        self.line = line
        self.pos = 0

        if len(self.line):
            self.cur = self.line[self.pos]
        else:
            self.cur = None

    def read_token(self):
        if self.cur is None:
            return Token(EOL, "")
        if self.cur == NONE:
            self.advance()
            return Token(NONE, NONE)
        elif self.cur in bombs:
            return self.read_bomb()
        elif self.cur in TYPES:
            temp = self.cur
            self.advance()
            return Token(TYPE, temp)
        elif self.cur in DIRECTIONS:
            temp = self.cur
            self.advance()
            return Token(DIRECTION, temp)
        elif self.cur in ACTIONS:
            temp = self.cur
            self.advance()
            return Token(ACTION, temp)
        elif self.cur in SOURCES:
            temp = self.cur
            self.advance()
            return Token(SOURCE, temp)
        elif self.cur in QUEUES:
            temp = self.cur
            self.advance()
            return Token(QUEUE, temp)

        raise Exception("Unknown token found : " + self.cur)

    def advance(self):
        self.pos += 1

        try:
            self.cur = self.line[self.pos]
        except IndexError:
            self.cur = None

    def read_bomb(self):
        res = ""

        while self.cur and self.cur in bombs:
            res += self.cur
            self.advance()

        return Token(BOMB, to_dec(res))

    def __repr__(self):
        return "Liner('{}',{},'{}')".format(self.line, self.pos, self.cur)


EXPLORER_ORDER = (TYPE, BOMB, DIRECTION, BOMB, ACTION, (SOURCE, BOMB), QUEUE, BOMB)
STRING_ORDER = ("type_", "duration", "direction", "delay", "action", ("source_", "amplitude"), "queue", "jump")
class LineParser:
    def __init__(self, liner_):
        self.liner = liner_
        self.token = self.liner.read_token()

    def eat(self, type_):
        if self.token.type == type_ or self.token.type == NONE:
            self.token = self.liner.read_token()
        else:
            raise Exception("Incorrect token found: looking for {}, found {} | {} at {}".format(type_, self.token.type, self.token.val, self.liner.pos))

    def get_explorers(self, index):
        return_explorers = []

        while self.token.type == TYPE:
            # source_text = None

            p = dict(
                index=index,
                type_=NONE,
                duration=NONE,
                direction=NONE,
                delay=NONE,
                action=NONE,
                source_=NONE,
                amplitude=NONE,
                queue=NONE,
                jump=NONE
            )

            for i in range(len(EXPLORER_ORDER)):
                if i > 1 and (self.token.type == TYPE or self.token.type == EOL):
                    break
                elif self.token.type == NONE:
                    self.eat(NONE)
                elif i == 5:
                    if self.token.type == SOURCE:
                        source_ = self.token.val
                        self.eat(SOURCE)

                        if source_ == INPUT:
                            try:
                                p["source_"] = input()
                            except EOFError:
                                raise Exception("No input entered")
                    elif self.token.type == BOMB or self.token.type == NONE:
                        p["amplitude"] = self.token.val
                        self.eat(BOMB)
                else:
                    if self.token.type == EXPLORER_ORDER[i]:
                        p[STRING_ORDER[i]] = self.token.val
                        self.eat(self.token.type)

            if p["direction"] == BOTH:
                del p["direction"]
                new_explorers = [Explorer(direction=UP, **p), Explorer(direction=DOWN, **p)]
            else:
                new_explorers = [Explorer(**p)]

            if p["queue"] == WAIT:
                return_explorers[-1].set_next(new_explorers)
            elif p["queue"] == LAST:
                global last_explorers
                last_explorers += new_explorers
            else:
                return_explorers += new_explorers

        return return_explorers

    def __repr__(self):
        return "LineParser({},{})".format(self.liner, self.token)


class Explorer:
    def __init__(self, index, type_, duration, direction, delay, action, source_, amplitude, queue, jump):
        self.index_ = index
        self.type = MODIFY if type_ == NONE else type_
        self.has_written = False

        self.duration = -1 if duration == NONE else duration
        self.direction = DOWN if direction == NONE else direction
        self.delay = 0 if delay == NONE else delay

        self.action = ADD if action == NONE else action
        self.previous = 0
        self.wave_index = 0

        self.source = source_
        self.is_sourced = self.source is not NONE

        self.amplitude = None if self.is_sourced else 1 if amplitude == NONE else amplitude
        self.queue = PUSH if queue == NONE else queue
        self.jump = 1 if jump == NONE else jump

        self.next = None

    def set_next(self, next_):
        if self.next:
            for each in self.next:
                each.set_next(next_)
        else:
            self.next = next_

    def get_modification(self):
        if self.is_sourced and len(self.source):
            amp = ASCII.index(self.source[0])
            self.source = self.source[1:]
            if not len(self.source):
                self.destroy()
        elif self.amplitude:
            amp = self.amplitude
        else:
            raise Exception("Explorer {} has no source or amplitude".format(self))

        if self.action == ADD:
            return amp
        elif self.action == SUBTRACT:
            return -amp
        elif self.action == INCREASING:
            self.previous += amp
            return self.previous
        elif self.action == DECREASING:
            self.previous -= amp
            return self.previous
        elif self.action == WAVE:
            if self.wave_index > 3:
                self.wave_index = 0

            if self.wave_index in (0, 2):
                temp = 0
            elif self.wave_index == 1:
                temp = amp
            elif self.wave_index == 3:
                temp = -amp
            else:
                temp = 0

            self.wave_index += 1
            return temp

    def tick(self):
        if self.delay > 0:
            self.delay -= 1
        else:
            if self.duration == 0:
                self.destroy()
            else:
                modification = self.get_modification()

                if self.type == MODIFY:
                    tape[self.index_] = ASCII[ASCII.index(tape[self.index_]) + modification]
                elif self.type == EXTEND:
                    if 0 <= self.index_ < len(tape):
                        tape[self.index_] = ASCII[ASCII.index(tape[self.index_]) + modification]
                    else:
                        tape.insert(self.index_, ASCII[modification])
                elif self.type == WRITE:
                    tape[self.index_] = ASCII[modification]
                elif self.type == OVERWRITE:
                    if 0 <= self.index_ < len(tape):
                        tape[self.index_] = ASCII[modification]
                    else:
                        tape.insert(self.index_, ASCII[modification])
                elif self.type == INSERT:
                    if self.has_written:
                        tape.insert(self.index_, ASCII[modification])

                        if self.direction == DOWN:
                            self.index_ -= 1
                    else:
                        tape[self.index_] = ASCII[modification]
                        self.has_written = True

                if self.direction == UP:
                    self.index_ -= self.jump
                elif self.direction == DOWN:
                    self.index_ += self.jump

            self.duration -= 1

    def destroy(self):
        if self.next:
            index = explorers.index(self)
            explorers.remove(self)
            explorers[index:index] = self.next
        else:
            explorers.remove(self)

    def __repr__(self):
        return "Explorer(index={},type_='{}',duration={},direction='{}',delay={},action='{}',source='{}',aplitude={},queue='{}',jump={},next={})"\
            .format(self.index_, self.type, self.duration, self.direction, self.delay, self.action, self.source, self.amplitude, self.queue, self.jump, self.next)


def to_bombs(dec):
    bomb = ""
    while dec:
        bomb = bombs[dec % length] + bomb
        dec //= length

    if not bomb:
        return "0"

    return bomb


def to_dec(bomb):
    cur_length = len(bomb)
    dec = 0

    for k in range(cur_length):
        cur = cur_length - k - 1
        dec += (length ** cur) * bombs.index(bomb[k])

    return dec

bombs = """0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"""
ASCII = ImmutableTape(""" !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~\n""")
length = len(bombs)

try:
    file = sys.argv[1]
except IndexError:
    file = "source.tnt"

source = open(file).read()
lines = source.split("\n")

tape = Tape(len(lines) * [" "])

last_explorers = []
explorers = []
last_used = False

for j in range(len(lines)):
    liner = Liner(lines[j])
    parser = LineParser(liner)
    explorers += parser.get_explorers(j)

while True:

    if not len(explorers):
        if last_used:
            if "-a" in sys.argv:
                print()

            break
        else:
            explorers = last_explorers
            last_used = True

    if "-a" in sys.argv:
        print("".join(tape))

    for explorer in explorers:
        explorer.tick()

print("".join(tape))

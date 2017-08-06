# Explode
Explode is a WIP tape-based esolang that is probably not Turing complete. Explore Explode at your own risk, because anything non-trivial may frustrate you more than you wish.

## Tape
The tape in Explode is finite. Every access attempt has its access index modulated by the length of the tape, so you cannot attempt to read outside the tape.

The tape is printed when the program terminates. It starts out as as many spaces as there are lines in your source. You can only modify the tape with explorers

##### Manipulating the Tape

The tape can contain the printable ASCII characters and newline. Each character's numeric value is its index in the following string:

```
 !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~
 
```

This string also acts like a tape, so subtracting `3` from `!` will result in `~`. The only way to modify the tape is with Explorer actions, which will add to or subtract from characters in the tape.

## Base-62

Numbers inside Explorers are in base-62, using the index in the following string:

```
0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
```

That means that decimal `1` is base-62 `1`, decimal `10` is base-62 `a`, decimal `50` is base-62 `O`, decimal `62` is base-62 `10`, etc. I think you know how bases work in math, and if you don't, go look it up before you keeping reading this.

## Ticks

Time in Explode is measured in ticks. Each tick notifies each active Explorer, in the order they were created. The program terminates when all Explorers are completed.

## Explorers

Explorers allow you to manipulate the tape. Explorers are placed to the right of the tape in any row, and can be placed one after the other. Explorers are formed as follows:

```
<type><duration><direction><delay><action><source|amplitude><queue><jump>
```

A space for a parameter usually indicates the default for that parameter. You may end the explorer creation statement early after the type is specified, and the rest will be filled in with defaults.

Explorers move around on the tape. They start at their index in the source code, and move based on their parameters. They only interact with their current cell on the tape.

##### Type

The type of an Explorer is how it interacts with the its current cell on the tape.

|     | Name | Description |
| --- | ---- | ----------- |
| `&` | Modify | Default. Add/subtract from the current value. |
| `%` | Extend | Add/subtract from the current value. If the target cell is out of the tape's bounds, insert a cell at the current position. |
| `=` | Write | Overwrite the current value. |
| `*` | Overwrite | Overwrite the current value. If the target cell is out of the tape's bounds, insert a cell at the current position. |
| `@` | Insert | Insert a cell at the current position*. |

Any non-trivial program will mostly utilize `&`, but the others are important for setting up.

\*The first run of an Insert Explorer will overwrite the current value instead of inserting.

##### Duration

The duration of an Explorer is a base-62 number that indicates how long the Explorer will run. The duration will only start ticking once the delay has ran out. A space indicates infinite duration.

##### Direction

The direction of an Explorer is how it will move on the tape.

|     | Name | Description |
| --- | ---- | ----------- |
| `_` | Down | Default. Move down (positive) in the tape. |
| `^` | Up | Move up (negative) in the tape. |
| `\|` | Both | Creates two Explorers with exactly the same parameters, except that one moves up and one moves down. They may not play will with each other.

Remember, when they reach the end of the tape, `Modify` and `Write` Explorers wrap on the tape, while `Extend` and `Insert` Explorers add to the tape.

##### Delay

The duration of an Explorer is a base-62 number that indicates how long the Explorer will . The delay will only start decreasing once the Explorer has been queued up to go. A space indicates no (`0`) delay.

##### Action

The action of an Explorer describes how it will affect the current cell.

|     | Name | Description |
| --- | ---- | ----------- |
| `+` | Add | Default. Add the source/amplitude. |
| `-` | Subtract | Subtract the source/amplitude. |
| `~` | Wave | Alternates doing nothing, adding the source/amplitude, doing nothing, and subtracting the source/amplitude. |
| `/` | Increasing | Sums the source/amplitudes up to this point, and adds the sum of them. |
| `\` | Decreasing | Sums the source/amplitudes up to this point, and subtracts the sum of them. |

##### Source/Amplitude

An Explorer can either have a source or an amplitude. One of these determines what the Explorer's values are.

The amplitude of an Explorer is a base-62 number describing the strength of the action. A space indicates an amplitude of `1`.

**Sources**

|     | Name | Description |
| --- | ---- | ----------- |
| `?` | Input | Reads a line of input from the user, and uses its characters' indexes in the ASCII tape, value by value, until it is empty. Note that both the duration and the source can destroy an Explorer. |

##### Queue

An Explorer does not need to be activated immediately. Instead, it can wait in line like a normal bot.

|     | Name | Description |
| --- | ---- | ----------- |
| `<` | Push | Default. The Explorer is activated upon program start (still waits for delay). |
| `>` | Wait | The Explorer waits until the previous Explorer in the current row has been destroyed to be activated. |
| `!` | Last | The Explorer graciously waits until all other Explorers are destroyed to activate. |

##### Jump

An Explorer does not have to move along the cells one-by-one. It can also jump along.

The jump of an Explorer is a base-62 number. This is how many cells it moves along each tick. A space indicates a jump of `1`.

## Sample Programs

This section will be added to as I push this language more.

**Hello, World!**

Prints `Hello, World!`. Each explorer adds each character's index in ASCII to the current index.

```
@1_0+E
@1_0+17
@1_0+1e
@1_0+1e
@1_0+1h
@1_0+c

@1_0+T
@1_0+1h
@1_0+1k
@1_0+1e
@1_0+16
@1_0+1
```

**cat**

Outputs one line of input.

```
@ _ +?
```

from abc import ABC, abstractmethod
from enum import Enum
import random


class Shot(Enum):
    MISS = 'Мимо'
    HIT = 'Попадание'
    SUNK = 'Корабль потоплен'


class Ship:
    def __init__(self, cells):
        self.__cells = frozenset(cells)
        self.__hits = set()

    @property
    def cells(self):
        return self.__cells

    @property
    def sunk(self):
        return self.__hits == self.__cells

    def hit(self, cell):
        if cell not in self.__cells:
            raise ValueError('Клетка не принадлежит кораблю')
        self.__hits.add(cell)


class Board:
    SIZE = 10
    FLEET = (4, 3, 3, 2, 2, 2, 1, 1, 1, 1)

    def __init__(self):
        self.__ships = []
        self.__shots = {}
        self.place_fleet()

    def place_fleet(self):
        if self.__shots:
            raise ValueError('Игра уже началась')
        while True:
            self.__ships.clear()
            for length in self.FLEET:
                occupied = {c for s in self.__ships for c in s.cells}
                candidates = []
                for r in range(self.SIZE):
                    for c in range(self.SIZE):
                        for dr, dc in ((0, 1), (1, 0)):
                            cells = [(r+i*dr, c+i*dc) for i in range(length)]
                            if all(0 <= x < self.SIZE and 0 <= y < self.SIZE and
                                   not any((x+a, y+b) in occupied for a in (-1,0,1) for b in (-1,0,1))
                                   for x,y in cells):
                                candidates.append(cells)
                if not candidates:
                    break
                self.__ships.append(Ship(random.choice(candidates)))
            else:
                return

    @property
    def defeated(self):
        return all(s.sunk for s in self.__ships)

    def available(self):
        return [(r,c) for r in range(self.SIZE) for c in range(self.SIZE) if (r,c) not in self.__shots]

    def fire(self, cell):
        if cell not in self.available():
            raise ValueError('Недопустимый или повторный выстрел')
        result = Shot.MISS
        for ship in self.__ships:
            if cell in ship.cells:
                ship.hit(cell)
                result = Shot.SUNK if ship.sunk else Shot.HIT
                break
        self.__shots[cell] = result
        return result

    def render(self, reveal=False):
        occupied = {c for s in self.__ships for c in s.cells}
        lines = ['   ' + ' '.join('ABCDEFGHIJ')]
        for r in range(self.SIZE):
            row = []
            for c in range(self.SIZE):
                cell = (r,c)
                shot = self.__shots.get(cell)
                row.append('o' if shot == Shot.MISS else 'X' if shot else '#' if reveal and cell in occupied else '.')
            lines.append(f'{r+1:2} ' + ' '.join(row))
        return '\n'.join(lines)


class Player(ABC):
    def __init__(self, name):
        self.name = name
        self.board = Board()

    @abstractmethod
    def choose_shot(self, target):
        pass


class HumanPlayer(Player):
    def choose_shot(self, target):
        while True:
            value = input('Координата (A1–J10, Q — выход): ').strip().upper()
            if value == 'Q':
                raise KeyboardInterrupt
            try:
                if len(value) < 2 or value[0] not in 'ABCDEFGHIJ':
                    raise ValueError
                cell = (int(value[1:])-1, ord(value[0])-ord('A'))
                if cell in target.available():
                    return cell
            except ValueError:
                pass
            print('Введите свободную клетку от A1 до J10.')


class ComputerPlayer(Player):
    def choose_shot(self, target):
        return random.choice(target.available())


class ConsoleUI:
    def show(self, human, computer):
        print('\nВаше поле:\n' + human.board.render(True))
        print('\nПоле противника:\n' + computer.board.render())
        print('. — неизвестно/пусто, # — корабль, X — попадание, o — промах')

    def announce(self, player, cell, result):
        r,c = cell
        print(f'{player.name}: {chr(65+c)}{r+1} — {result.value}')


class Game:
    def __init__(self):
        self.human = HumanPlayer('Игрок')
        self.computer = ComputerPlayer('Компьютер')
        self.ui = ConsoleUI()

    def run(self):
        current, opponent = self.human, self.computer
        while True:
            if current is self.human:
                self.ui.show(self.human, self.computer)
            cell = current.choose_shot(opponent.board)
            result = opponent.board.fire(cell)
            self.ui.announce(current, cell, result)
            if opponent.board.defeated:
                self.ui.show(self.human, self.computer)
                print(f'Победитель: {current.name}!')
                return
            if result == Shot.MISS:
                current, opponent = opponent, current


if __name__ == '__main__':
    try:
        Game().run()
    except (KeyboardInterrupt, EOFError):
        print('\nИгра завершена.')

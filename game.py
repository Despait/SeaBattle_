import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
import random
from core import Board, Player, Shot

class Weapon(ABC):
    name = ''
    @abstractmethod
    def cells(self, cell): ...
    def attack(self, board, cell):
        return [(p, board.fire(p)) for p in self.cells(cell) if p in board.available()]

class Cannon(Weapon):
    name = 'Орудие'
    def cells(self, cell): return [cell]

class Torpedo(Weapon):
    name = 'Торпеда'
    def cells(self, cell):
        r,c = cell
        return [(r,c+i) for i in range(-1,2)]

class Airstrike(Weapon):
    name = 'Авиаудар'
    def cells(self, cell):
        r,c = cell
        return [(r+i,c+j) for i in range(-1,2) for j in range(-1,2)]

class Admiral(Player):
    def choose_shot(self, target): return random.choice(target.available())

class TacticalAI(Player):
    def __init__(self, level):
        super().__init__('Адмирал ИИ'); self.level = level; self.hits = set()
    def choose_shot(self, target):
        free = set(target.available())
        neighbors = {(r+a,c+b) for r,c in self.hits for a,b in ((1,0),(-1,0),(0,1),(0,-1))} & free
        if self.level != 'Лёгкий' and neighbors: return random.choice(sorted(neighbors))
        parity = {p for p in free if sum(p)%2 == 0}
        return random.choice(sorted(parity if self.level == 'Сложный' and parity else free))
    def observe(self, cell, result):
        if result == Shot.HIT: self.hits.add(cell)
        elif result == Shot.SUNK: self.hits.clear()

class Battle:
    def __init__(self, level):
        self.human = Admiral('Игрок'); self.ai = TacticalAI(level)
        self.weapons = [Cannon(), Torpedo(), Airstrike()]; self.__ammo = [None, 3, 1]
        self.turns = 0; self.hits = 0; self.winner = None
    @property
    def ammo(self): return tuple(self.__ammo)
    def play(self, index, cell):
        if self.winner or cell not in self.ai.board.available() or self.__ammo[index] == 0: return [], None
        results = self.weapons[index].attack(self.ai.board, cell)
        if self.__ammo[index] is not None: self.__ammo[index] -= 1
        self.turns += 1; self.hits += sum(s != Shot.MISS for _,s in results)
        if self.ai.board.defeated: self.winner = 'Игрок'; return results, None
        p = self.ai.choose_shot(self.human.board); s = self.human.board.fire(p); self.ai.observe(p,s)
        if self.human.board.defeated: self.winner = 'Компьютер'
        return results, (p,s)

class NavalUI:
    def __init__(self, root):
        self.root = root; root.title('Морской бой: MAX'); root.configure(bg='#10243a'); root.resizable(False,False)
        self.level = tk.StringVar(value='Средний'); self.weapon = tk.IntVar(value=0)
        bar = ttk.Frame(root,padding=12); bar.pack(fill='x')
        ttk.Label(bar,text='МОРСКОЙ БОЙ / MAX',font=('Arial',19,'bold')).pack(side='left')
        ttk.Combobox(bar,textvariable=self.level,values=['Лёгкий','Средний','Сложный'],state='readonly',width=10).pack(side='right')
        ttk.Button(bar,text='Новая битва',command=self.reset).pack(side='right',padx=8)
        self.canvas = tk.Canvas(root,width=820,height=395,bg='#10243a',highlightthickness=0); self.canvas.pack(); self.canvas.bind('<Button-1>',self.click)
        controls = ttk.Frame(root,padding=10); controls.pack(fill='x'); self.buttons=[]
        for i,w in enumerate(['Орудие','Торпеда','Авиаудар']):
            b=ttk.Radiobutton(controls,text=w,variable=self.weapon,value=i); b.pack(side='left',padx=10); self.buttons.append(b)
        self.stats=ttk.Label(controls); self.stats.pack(side='right')
        self.log=tk.Text(root,height=7,width=100,bg='#081726',fg='#d9efff',font=('Consolas',10),state='disabled'); self.log.pack(fill='x',padx=12,pady=12)
        self.reset()
    def message(self,text):
        self.log.configure(state='normal'); self.log.insert('end',text+'\n'); self.log.see('end'); self.log.configure(state='disabled')
    def reset(self):
        self.battle=Battle(self.level.get()); self.weapon.set(0); self.log.configure(state='normal'); self.log.delete('1.0','end'); self.log.configure(state='disabled'); self.message('Флот готов. Выберите оружие и клетку противника.'); self.draw()
    def draw(self):
        self.canvas.delete('all')
        for x,board,reveal,title in [(35,self.battle.human.board,True,'ВАШ ФЛОТ'),(445,self.battle.ai.board,False,'ПРОТИВНИК')]:
            self.canvas.create_text(x+165,18,text=title,fill='#a8ddff',font=('Arial',14,'bold'))
            rows=board.render(reveal).splitlines()[1:]
            for i in range(10):
                self.canvas.create_text(x+16+i*33,40,text=chr(65+i),fill='white'); self.canvas.create_text(x-13,66+i*33,text=str(i+1),fill='white')
                for j,s in enumerate(rows[i].split()[1:]):
                    X=x+j*33; Y=50+i*33
                    self.canvas.create_rectangle(X,Y,X+32,Y+32,fill={'.':'#1c5278','#':'#64958b','X':'#dc514f','o':'#20364b'}[s],outline='#365f7e')
                    if s in 'Xo': self.canvas.create_text(X+16,Y+16,text='×' if s=='X' else '·',fill='white',font=('Arial',18,'bold'))
        for i,b in enumerate(self.buttons):
            a=self.battle.ammo[i]; b.configure(text=self.battle.weapons[i].name+' ('+('∞' if a is None else str(a))+')',state='disabled' if a==0 or self.battle.winner else 'normal')
        if self.battle.ammo[self.weapon.get()]==0: self.weapon.set(0)
        self.stats.configure(text=f'Ходы: {self.battle.turns}   Попадания: {self.battle.hits}')
    def click(self,event):
        r=(event.y-50)//33; c=(event.x-445)//33
        if not (0<=r<10 and 0<=c<10): return
        results,reply=self.battle.play(self.weapon.get(),(r,c))
        if not results: return
        for (a,b),s in results: self.message(f'Вы: {chr(65+b)}{a+1} — {s.value}')
        if reply:
            (a,b),s=reply; self.message(f'ИИ: {chr(65+b)}{a+1} — {s.value}')
        if self.battle.winner: self.message('Победитель: '+self.battle.winner+'!')
        self.draw()

if __name__=='__main__':
    root=tk.Tk(); NavalUI(root); root.mainloop()

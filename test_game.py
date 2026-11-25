import unittest
from core import Board, Ship, Shot
from game import Cannon, Torpedo, Airstrike, Battle
class UnitTests(unittest.TestCase):
 def test_ship(self):
  s=Ship([(0,0),(0,1)]); s.hit((0,0)); self.assertFalse(s.sunk); s.hit((0,1)); self.assertTrue(s.sunk)
 def test_invalid_hit(self):
  with self.assertRaises(ValueError): Ship([(0,0)]).hit((1,1))
 def test_weapons(self):
  self.assertEqual(Cannon().cells((0,0)),[(0,0)])
  self.assertEqual(len(Torpedo().cells((5,5))),3)
  self.assertEqual(len(Airstrike().cells((5,5))),9)
 def test_repeat(self):
  b=Board(); b.fire((0,0))
  with self.assertRaises(ValueError): b.fire((0,0))
 def test_boundary(self):
  b=Board()
  with self.assertRaises(ValueError): b.fire((-1,0))
 def test_corner_attack(self):
  b=Board(); self.assertEqual(len(Airstrike().attack(b,(0,0))),4)
class ScenarioTests(unittest.TestCase):
 def test_ammo_and_repeated_action(self):
  b=Battle('Средний'); b.play(1,(0,0)); self.assertEqual(b.ammo[1],2); self.assertEqual(b.turns,1)
  self.assertEqual(b.play(1,(0,0)),([],None)); self.assertEqual(b.turns,1)
 def test_complete_battle(self):
  b=Battle('Лёгкий')
  for r in range(10):
   for c in range(10):
    if not b.winner: b.play(0,(r,c))
  self.assertIn(b.winner,['Игрок','Компьютер'])
  n=b.turns; self.assertEqual(b.play(0,(0,0)),([],None)); self.assertEqual(b.turns,n)
if __name__=='__main__': unittest.main(verbosity=2)

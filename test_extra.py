import unittest
from unittest.mock import patch
from core import Board, Ship, Shot
from game import Battle, Torpedo
class AdditionalTests(unittest.TestCase):
 def test_miss(self):
  with patch.object(Board,'place_fleet'):
   b=Board(); self.assertEqual(b.fire((0,0)),Shot.MISS)
 def test_hit_then_sunk(self):
  with patch.object(Board,'place_fleet'):
   b=Board(); b._Board__ships=[Ship([(0,0),(0,1)])]
   self.assertEqual(b.fire((0,0)),Shot.HIT)
   self.assertEqual(b.fire((0,1)),Shot.SUNK)
   self.assertTrue(b.defeated)
 def test_torpedo_edge(self):
  b=Board(); self.assertEqual(len(Torpedo().attack(b,(0,0))),2)
 def test_exhausted_ammo(self):
  b=Battle('Средний'); b.play(2,(0,0)); n=b.turns
  self.assertEqual(b.ammo[2],0)
  self.assertEqual(b.play(2,(9,9)),([],None)); self.assertEqual(b.turns,n)

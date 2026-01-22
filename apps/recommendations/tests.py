from django.test import TestCase
from .utils import calculate_match_score
from .models import ColorMatchingRule
from types import SimpleNamespace

class RecommendationLogicTest(TestCase):
    def setUp(self):
        # Seed the rules that we expect to exist
        ColorMatchingRule.objects.create(color_1='red', color_2='green', score=0.20)
        ColorMatchingRule.objects.create(color_1='black', color_2='white', score=0.90)
        ColorMatchingRule.objects.create(color_1='blue', color_2='white', score=0.85)

    def test_color_rules(self):
        # Mock objects with .color attribute
        red_top = SimpleNamespace(color="Red")
        green_bottom = SimpleNamespace(color="Green")
        
        black_top = SimpleNamespace(color="Black")
        white_bottom = SimpleNamespace(color="White")
        
        blue_top = SimpleNamespace(color="Blue")
        
        purple_top = SimpleNamespace(color="Purple")
        orange_bottom = SimpleNamespace(color="Orange")

        # Test Case 1: Red + Green (Should be 0.20)
        score_rg = calculate_match_score(red_top, green_bottom)
        self.assertEqual(score_rg, 0.20)

        # Test Case 2: Black + White (Should be 0.90)
        score_bw = calculate_match_score(black_top, white_bottom)
        self.assertEqual(score_bw, 0.90)

        # Test Case 3: Blue + White (Should be 0.85)
        score_bluew = calculate_match_score(blue_top, white_bottom)
        self.assertEqual(score_bluew, 0.85)

        # Test Case 4: Fallback (Purple + Orange) - Should not be None
        # It will be 0.40 (fallback) or ML score
        score_po = calculate_match_score(purple_top, orange_bottom)
        self.assertIsNotNone(score_po)

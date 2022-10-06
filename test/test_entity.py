from random import random, uniform
from unittest import TestCase, skip

# noinspection PyProtectedMember
from mock import Mock, MagicMock, patch, call

from maic.entity import Entity
from maic.entitylist import EntityList
from maic.constants import T_METHOD_NONE


class TestEntity(TestCase):

    def test_entity_scores_one(self):
        """Check that an Entity has a default score of 1."""
        test_object = Entity("A")
        self.assertEqual(1, test_object.score, "Default Entity score is 1")

    def test_entity_scores_is_settable(self):
        """Check that an Entity score can be set."""
        set_score = 99.3
        test_object = Entity("A")
        test_object.score = set_score
        self.assertEqual(set_score, test_object.score,
                         "Entity score should be 99.3")

    def test_entity_has_transformed_score_one(self):
        """Check that an Entity has a default transformed score of 0."""
        test_object = Entity("A")
        self.assertEqual(0, test_object.transformed_score(),
                         "Default Entity transformed score is 0")

    def test_entity_transformed_score_uses_adjusted_scores_dict(self):
        """Check that an Entity transformed score is derived from the
        adjusted_scores dictionary."""
        set_score = (random() * 1000) + 1.0
        transform_method = "Bongo"
        test_object = Entity("A")
        test_object.adjusted_scores[transform_method] = set_score
        self.assertEqual(set_score,
                         test_object.transformed_score(transform_method),
                         "Entity score should be %f" % set_score)

    def test_entity_transformed_score_default_for_incorrect_method_name(self):
        """Check that an Entity transformed score of zero is returned for a
        non-calculated method"""
        set_score = (random() * 1000) + 1.0
        transform_method = "Bongo"
        wrong_transform_method = "wrong"
        test_object = Entity("A")
        test_object.adjusted_scores[transform_method] = set_score
        self.assertEqual(0,
                         test_object.transformed_score(wrong_transform_method),
                         "Entity score should be %f" % 0)

    def test_entity_transformed_score_defaults_to_key_none(self):
        """Check that when we ask for a transformed_score with no specifier
        as to the method used, we get the value back from the dictionary
        using key T_METHOD_NONE"""
        set_score = (random() * 1000) + 1.0
        test_object = Entity("A")
        test_object.adjusted_scores[T_METHOD_NONE] = set_score
        self.assertEqual(set_score,
                         test_object.transformed_score(),
                         "Entity score should be %f" % set_score)

    def test_entity_owned_list_is_empty_by_default(self):
        """Check that Entity knows of no lists by default."""
        test_object = Entity("A")
        self.assertFalse(test_object.lists,
                         "Default List in an Entity should be empty")

    def test_none_is_invalid_entity_name(self):
        """Check that Entity throws an error with None as name."""
        try:
            Entity(None)
            raise Exception("Should not get here because None is an invalid "
                            "Entity name")
        except AssertionError:
            pass

    def test_empty_string_is_invalid_entity_name(self):
        """Check that Entity throws an error with empty string as name."""
        try:
            Entity("")
            raise Exception("Should not get here because empty string is an "
                            "invalid Entity name")
        except AssertionError:
            pass

    def test_different_object_with_same_name(self):
        """Test that two Entity objects with the same name are different."""
        test_object1 = Entity("A")
        test_object2 = Entity("A")
        self.assertTrue(test_object1 != test_object2)

    def test_calculate_new_score_drops_to_zero(self):
        """
        Test that an Entity calculates its new score as zero by default.

        A default Entity has no lists to which it belongs thus its score is
        zero.
        """
        test_object = Entity("BB")
        test_object.calculate_new_score()
        self.assertEqual(0, test_object.score, "Score should now be zero")

    def test_calculate_new_score_sums_list_scores_correctly(self):
        """
        Test that an Entity calculates its new score as the sum of the scores
        of the lists that mention it.
        """
        test_object = Entity("BB")
        list1 = EntityList()
        list1.weight = 1.7
        list1.append(test_object)

        list2 = EntityList()
        list2.weight = 9.3
        list2.append(test_object)

        list3 = EntityList()
        list3.weight = 6.112
        list3.append(test_object)

        test_object.calculate_new_score()
        self.assertAlmostEqual(
            17.112,
            test_object.score,
            3,
            "Score should now be the sum of the list scores")

    def test_calculate_new_score_accounts_for_categories(self):
        """
        Test that an Entity calculates its new score as the sum of the
        scores of the lists that mention it, allowing for the category of
        the list.
        """
        test_object = Entity("BB")
        list1 = EntityList()
        list1.category_name = "type1"
        list1.weight = 1.7
        list1.append(test_object)

        list2 = EntityList()
        list2.category_name = "type2"
        list2.weight = 9.3
        list2.append(test_object)

        list3 = EntityList()
        list3.category_name = "type2"
        list3.weight = 6.112
        list3.append(test_object)

        test_object.calculate_new_score()
        self.assertAlmostEqual(
            11.0,
            test_object.score,
            1,
            "Score should now be the sum of the highest list scores in"
            "each category {}".format(test_object.score))

    def test_calculate_new_score_accounts_for_categories_opposite_order(self):
        """
        Test that an Entity calculates its new score as the sum of the
        scores of the lists that mention it, regardless of the order of the
        EntityList objects
        """
        test_object = Entity("BB")
        list1 = EntityList()
        list1.category_name = "type1"
        list1.weight = 1.7
        list1.append(test_object)

        list2 = EntityList()
        list2.category_name = "type2"
        list2.weight = 6.112
        list2.append(test_object)

        list3 = EntityList()
        list3.category_name = "type2"
        list3.weight = 9.3
        list3.append(test_object)

        test_object.calculate_new_score()
        self.assertAlmostEqual(
            11.0,
            test_object.score,
            1,
            "Score should now be the sum of the highest list scores in"
            "each category {}".format(test_object.score))

    def test_list_added_is_stored(self):
        """Test that when an Entity is added to an EntityList, the list is
        stored in the Entity and can be retrieved
        """
        test_object = Entity("CC")
        list1 = EntityList()
        test_object.note_list(list1)

        self.assertEqual(1, len(test_object.lists), "Should be one entry in "
                                                    "the list of lists")
        self.assertTrue(list1 in test_object.lists, "List should be in the "
                                                    "list of lists")

    def test_list_added_is_stored_only_once(self):
        """Test that when an Entity is added to an EntityList more than once,
        the list is stored in the Entity and can be retrieved just once
        """
        test_object = Entity("CC")
        list1 = EntityList()
        test_object.note_list(list1)
        test_object.note_list(list1)
        test_object.note_list(list1)

        self.assertEqual(1, len(test_object.lists), "Should be one entry in "
                                                    "the list of lists")
        self.assertTrue(list1 in test_object.lists, "List should be in the "
                                                    "list of lists")

    def test_entity_knows_contributing_list_components(self):
        """Check that an Entity knows which lists contributed what weights to
        its overall score"""
        test_object = Entity("DD")
        list1 = EntityList()
        list1.category_name = "type1"
        list1.weight = 4.3
        list1.append(test_object)

        list2 = EntityList()
        list2.category_name = "type2"
        list2.weight = 6.112
        list2.append(test_object)

        list3 = EntityList()
        list3.category_name = "type2"
        list3.weight = 9.3
        list3.append(test_object)

        unrelated_list = EntityList()
        unrelated_list.category_name = "type1"
        unrelated_list.weight = 99.42

        test_object.calculate_new_score()

        self.assertEqual(4.3, test_object.score_from_list(list1),
                         "Expected 4.3 from list1")
        self.assertEqual(0.0, test_object.score_from_list(list2),
                         "Expected 0.0 from list2")
        self.assertEqual(9.3, test_object.score_from_list(list3),
                         "Expected 9.3 from list3")
        self.assertEqual(0.0, test_object.score_from_list(unrelated_list),
                         "Expected 0.0 from unrelated_list")

    def test_entity_reports_raw_scores(self):
        """Check that an Entity reports the scores from each list regardless
        of winning category"""
        test_object = Entity("DD")
        list1 = EntityList()
        list1.category_name = "type1"
        list1.weight = 4.3
        list1.append(test_object)

        list2 = EntityList()
        list2.category_name = "type2"
        list2.weight = 6.112
        list2.append(test_object)

        list3 = EntityList()
        list3.category_name = "type2"
        list3.weight = 9.3
        list3.append(test_object)

        unrelated_list = EntityList()
        unrelated_list.category_name = "type1"
        unrelated_list.weight = 99.42

        test_object.calculate_new_score()

        self.assertEqual(4.3, test_object.raw_score_from_list(list1),
                         "Expected 4.3 from list1")
        self.assertEqual(6.112, test_object.raw_score_from_list(list2),
                         "Expected 6.112 from list2")
        self.assertEqual(9.3, test_object.raw_score_from_list(list3),
                         "Expected 9.3 from list3")
        self.assertEqual(0.0, test_object.raw_score_from_list(unrelated_list),
                         "Expected 0.0 from unrelated_list")

    def test_reset(self):
        """Check that we can reset an Entity score and other parameters in
        readiness for another analysis run"""
        test_object = Entity("BB")
        list1 = EntityList()
        list1.category_name = "type1"
        list1.weight = 1.7
        list1.append(test_object)

        list2 = EntityList()
        list2.category_name = "type2"
        list2.weight = 6.112
        list2.append(test_object)

        list3 = EntityList()
        list3.category_name = "type2"
        list3.weight = 9.3
        list3.append(test_object)

        test_object.calculate_new_score()
        self.assertAlmostEqual(
            11.0,
            test_object.score,
            1,
            "Score should now be the sum of the highest list scores in"
            "each category {}".format(test_object.score))

        test_object.reset()
        self.assertAlmostEqual(
            1,
            test_object.score,
            10,
            "Score should now be reset to 1")
        self.assertEqual(0.0, test_object.score_from_list(list1),
                         "Expected 4.3 from list1")
        self.assertEqual(0.0, test_object.score_from_list(list2),
                         "Expected 0.0 from list2")
        self.assertEqual(0.0, test_object.score_from_list(list3),
                         "Expected 9.3 from list3")

    def test_sum_weights(self):
        """Test that the sum_weights() function calculates correctly"""
        from random import randint, uniform
        weights = {}
        expected_sum = 0.0
        for category in ['cat1', 'cat2', 'cat3']:
            weights[category] = []
            count = randint(3, 6)
            for n in range(count):
                weights[category].append(uniform(0, 20))
            expected_sum += max(weights[category])
        test_object = Entity("ZZ")
        self.assertEqual(expected_sum,
                         test_object.sum_max_weights_per_category(weights))

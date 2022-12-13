from math import sqrt
from random import uniform
from re import compile
from unittest import TestCase, skip

import numpy as np
from mock import MagicMock, patch

from maic.entity import Entity
from maic.entitylist import EntityList, ExponentialEntityList, adjusted_weight, \
    FAILED_RANKED_LIST_DESCENT_STEP


class TestEntityList(TestCase):

    def test_entitylist_is_empty_by_default(self):
        """Check that EntityList object is empty by default."""
        test_object = EntityList()
        self.assertFalse(test_object, "Default EntityList should be empty")

    def test_entitylist_has_initial_weight_one(self):
        """Check that an EntityList object has a weight of 1 by default."""
        test_object = EntityList()
        self.assertEqual(1, test_object.weight,
                         "Default EntityList weight should be one")

    def test_empty_entitylist_reverts_to_weight_zero(self):
        """Check that an empty EntityList calculates its new weight as zero."""
        test_object = EntityList()
        test_object.calculate_new_weight()
        self.assertEqual(0.0, test_object.weight,
                         "Weight should revert to zero")
        self.assertEqual(-1.0, test_object.delta, "Delta should be -1.0")

    def test_entitylist_calculates_weight_from_entities(self):
        """
        Check that an EntityList calculates its new weight from the Entities
        it contains
        """
        test_object = EntityList()
        ent1 = Entity("1")
        ent1.score = 2.4
        test_object.append(ent1)
        ent2 = Entity("2")
        ent2.score = 14.2
        test_object.append(ent2)
        returned_delta = test_object.calculate_new_weight()
        self.assertAlmostEqual(2.88097206, test_object.weight, 8,
                               "Weight should be calculated as 2.88097206")
        self.assertAlmostEqual(1.88097206, test_object.delta, 8,
                               "Delta should be 1.88097206")
        self.assertAlmostEqual(1.88097206, returned_delta, 8,
                               "Returned Delta should be 1.88097206")

    def test_entitylist_returns_absolute_delta_value(self):
        """
        Check that an EntityList calculates its new weight from the Entities
        it contains and stores the real delta i.e. delta can be negative
        """
        test_object = EntityList()
        ent1 = Entity("1")
        ent1.score = 0.4
        test_object.append(ent1)
        ent2 = Entity("2")
        ent2.score = 0.3
        test_object.append(ent2)
        returned_delta = test_object.calculate_new_weight()
        self.assertAlmostEqual(0.59160797831, test_object.weight, 8,
                               "Weight should be calculated as 0.59160797831")
        self.assertAlmostEqual(-0.40839202169, test_object.delta, 8,
                               "Delta should be -0.40839202169")
        self.assertAlmostEqual(-0.40839202169, returned_delta, 8,
                               "Returned Delta should be -0.40839202169")

    def test_entitylist_reset(self):
        """
        Check that an EntityList can be reset having first calculated a weight
        """
        test_object = EntityList()
        ent1 = MagicMock(Entity)
        ent1.score = 2.4
        test_object.append(ent1)
        ent2 = MagicMock(Entity)
        ent2.score = 14.2
        test_object.append(ent2)
        test_object.calculate_new_weight()
        self.assertAlmostEqual(2.88097206, test_object.weight, 8,
                               "Weight should be calculated as 2.88097206")
        self.assertAlmostEqual(1.88097206, test_object.delta, 8,
                               "Delta should be 1.88097206")
        test_object.reset()
        self.assertEqual(1, test_object.weight, "Weight should be reset to 1")
        self.assertIsNone(test_object.delta, "Delta should be reset to None")
        # self.assertEqual(0.0, test_object.__total_entity_weight,
        #                  "Total Entity Weight should be zero")
        ent1.reset.assert_called_once()
        ent2.reset.assert_called_once()

    def test_entitylist_calls_fit_curves_after_calculating_weight(self):
        """
        Check that an EntityList calls the _fit_curve_to_entity_scores()
        method after calculating the new list weight
        """

        class FakeEntityList(EntityList):

            def __init__(self):
                super(FakeEntityList, self).__init__()
                self.hit_successfully = False

            def _fit_curve_to_entity_scores(self):
                self.hit_successfully = True

        test_object = FakeEntityList()
        self.assertFalse(test_object.hit_successfully,
                         "hit_successfully should be false by default")
        test_object.calculate_new_weight()
        self.assertTrue(test_object.hit_successfully,
                        "Should have gone through the "
                        "_fit_curve_to_entity_scores() method")

    def test_entitylist_reports_adjusted_weight_for_given_score(self):
        """
        Given a score for an Entity (assumed to be in the list), return the
        weight of the list as if that score were not included.
        """
        test_object = EntityList()
        ent1 = Entity("1")
        ent1.score = 2.4
        test_object.append(ent1)
        ent2 = Entity("2")
        ent2.score = 14.2
        test_object.append(ent2)
        test_object.calculate_new_weight()
        self.assertAlmostEqual(sqrt(2.4),
                               test_object.get_corrected_list_weight(
                                   ent2.score), 1,
                               "Corrected weight should be sqrt(2.4)")
        self.assertAlmostEqual(sqrt(14.2),
                               test_object.get_corrected_list_weight(
                                   ent1.score), 1,
                               "Corrected weight should be sqrt(14.2)")

    def test_entitylist_reports_zero_weight_for_single_entity_entitylist(self):
        """
        Given a score for an Entity (the only entity in the list), return the
        weight of the list as if that score were not included i.e. zero.
        """
        test_object = EntityList()
        ent1 = Entity("1")
        ent1.score = 96.4
        test_object.append(ent1)
        test_object.calculate_new_weight()
        self.assertAlmostEqual(0, test_object.get_corrected_list_weight(
            ent1.score), 1, "Corrected weight should be 0")

    def test_entitylist_fails_adjusted_weight_on_empty_entitylist(self):
        """
        Check that the get_corrected_list_weight() method fails with an
        exception on an empty list.
        """
        test_object = EntityList()
        ent1 = Entity("1")
        ent1.score = 96.4
        # test_object.append(ent1)
        test_object.calculate_new_weight()
        try:
            test_object.get_corrected_list_weight(ent1.score)
            raise Exception("Should have thrown an Exception")
        except ValueError:
            pass
        except Exception:
            raise Exception("Should have thrown a ValueError")

    def test_entitylist_is_unranked_by_default(self):
        """Check that the default setting is 'unranked'"""
        test_object = EntityList()
        self.assertFalse(test_object.is_ranked,
                         "Default EntityList should be unranked")

    def test_entitylist_can_be_set_ranked(self):
        """Check that we can set the ranked attribute"""
        test_object = EntityList()
        test_object.is_ranked = True
        self.assertTrue(test_object.is_ranked,
                        "Should be possible to set an EntityList as ranked")

    def test_entity_can_be_appended_to_entitylist(self):
        """
        Check that appending an Entity to the List extends the list and stores
        reference to the list in the Entity.
        """
        test_entity = Entity("D")
        test_object = EntityList()
        test_object.append(test_entity)
        self.assertTrue(test_object, "List should now be true")
        self.assertEqual(1, len(test_object),
                         "List should contain one element")
        self.assertTrue(test_entity in test_object,
                        "Entity should be in the EntityList")
        self.assertTrue(test_entity.lists, "Entity's lists should now be True")
        self.assertEqual(1, len(test_entity.lists),
                         "Entity's List of Lists should contain one element")
        self.assertTrue(test_object in test_entity.lists,
                        "EntityList should be in the Entity's List of Lists")

    def test_entitylist_category_name_is_empty_by_default(self):
        """Check that an EntityList category name is blank by default"""
        test_object = EntityList()
        self.assertIsNotNone(test_object.category_name,
                             "Category name should not be None")
        self.assertFalse(test_object.category_name,
                         "Category name should be empty by default")

    def test_category_name_is_trimmed_left(self):
        """Check that an EntityList category name has leading space trimmed"""
        test_object = EntityList()
        test_object.category_name = "   ABC"
        self.assertEqual("ABC", test_object.category_name,
                         "Category name should have leading space trimmed")

    def test_category_name_is_trimmed_right(self):
        """Check that an EntityList category name has trailing space trimmed"""
        test_object = EntityList()
        test_object.category_name = "DEF    "
        self.assertEqual("DEF", test_object.category_name,
                         "Category name should have trailing space trimmed")

    def test_category_name_is_trimmed_both(self):
        """Check that an EntityList category name has both leading and
        trailing space trimmed"""
        test_object = EntityList()
        test_object.category_name = "   XYZ   other   "
        self.assertEqual("XYZ   other", test_object.category_name,
                         "Category name should have leading and trailing "
                         "space trimmed")

    def test_category_is_unknown_number_by_default(self):
        """
        Check that the category of an EntityList is of the pattern
        'Unknown-nnn' by default
        """
        test_object = EntityList()
        expected_pattern = compile("^Unknown-[0-9]{3}$")
        # noinspection PyUnresolvedReferences
        self.assertIsNotNone(test_object.category,
                             "Category should not be None")
        # noinspection PyUnresolvedReferences
        self.assertTrue(expected_pattern.match(test_object.category),
                        "Category should match 'Unknown-nnn' by default "
                        "- got '{}'".format(test_object.category))

    def test_two_lists_have_different_categories_by_default(self):
        """
        Check that two EntityLists with no category name specified have
        different categories reported.
        """
        test_object1 = EntityList()
        test_object2 = EntityList()
        # noinspection PyUnresolvedReferences
        self.assertTrue(test_object1.category != test_object2.category,
                        "Categories should be unique to each list by default")

    def test_category_cannot_be_set_directly(self):
        """Check that the category of an EntityList cannot be set directly"""
        test_object = EntityList()
        try:
            test_object.category = "ABC"
            self.fail("Should have thrown an AttributeError")
        except AttributeError:
            pass

    def test_category_converts_to_uppercase_when_set(self):
        """
        Check that the category of an EntityList can be set as a by-product
        of the category_name and
        the reported value is uppercase
        """
        test_object = EntityList()
        test_object.category_name = "def"
        # noinspection PyUnresolvedReferences
        self.assertEqual("DEF", test_object.category, "Category should be DEF")

    def test_category_is_trimmed_left(self):
        """
        Check that an EntityList category has leading space trimmed as a
        by-product of the category name
        """
        test_object = EntityList()
        test_object.category_name = "   ABC"
        # noinspection PyUnresolvedReferences
        self.assertEqual("ABC", test_object.category,
                         "Category should have leading space trimmed")

    def test_category_is_trimmed_right(self):
        """
        Check that an EntityList category has trailing space trimmed as a
        by-product of the category name
        """
        test_object = EntityList()
        test_object.category_name = "DEF    "
        # noinspection PyUnresolvedReferences
        self.assertEqual("DEF", test_object.category,
                         "Category should have trailing space trimmed")

    def test_category_is_trimmed_both_and_internally_subbed(self):
        """
        Check that an EntityList category has all space trimmed/replaced as
        a by-product of the category name.

        Leading/trailing space is discarded and internal spaces are
        converted to hyphens
        """
        test_object = EntityList()
        test_object.category_name = "   XYZ   other   "
        # noinspection PyUnresolvedReferences
        self.assertEqual("XYZ-OTHER", test_object.category,
                         "Category name should have leading and trailing "
                         "space trimmed")

    def test_entitylist_name_is_empty_by_default(self):
        """Check that an EntityList name is blank by default"""
        test_object = EntityList()
        self.assertIsNotNone(test_object.name, "Name should not be None")
        self.assertFalse(test_object.name, "Name should be empty by default")

    def test_entitylist_name_is_trimmed_left(self):
        """Check that an EntityList name has leading space trimmed"""
        test_object = EntityList()
        test_object.name = "   ABC"
        self.assertEqual("ABC", test_object.name,
                         "Name should have leading space trimmed")

    def test_entitylist_name_is_trimmed_right(self):
        """Check that an EntityList name has trailing space trimmed"""
        test_object = EntityList()
        test_object.name = "DEF    "
        self.assertEqual("DEF", test_object.name,
                         "Name should have trailing space trimmed")

    def test_entitylist_name_is_trimmed_both(self):
        """Check that an EntityList name has both leading and
        trailing space trimmed"""
        test_object = EntityList()
        test_object.name = "   XYZ   other   "
        self.assertEqual("XYZ   other", test_object.name,
                         "Name should have leading and trailing space trimmed")

    def test_weight_for_entity_reports_zero_for_none_entity(self):
        """Check that an EntityList returns zero when asked for the
        weight for a None Entity"""
        test_object = EntityList()
        self.assertEqual(0.0, test_object.get_weight_for_entity(None),
                         "Should return zero for a None entity")

    def test_weight_for_entity_reports_zero_for_noncontained_entity(self):
        """Check that an EntityList returns zero when asked for the
        weight for a Entity that is not in its list of Entities"""
        test_object = EntityList()
        ent1 = Entity("1")
        test_object.append(ent1)

        ent2 = Entity("2")
        test_object.append(ent2)

        uncontained = Entity("3")
        self.assertEqual(0.0, test_object.get_weight_for_entity(uncontained),
                         "Should return zero for a entity not in the list")

    def test_weight_for_entity_uses_method_call_for_contained_entity(self):
        """Check that an EntityList calls its internal method when asked for
        the
        weight for a Entity that is in its list of Entities"""

        class FakeEntityList(EntityList):

            def __init__(self):
                super(FakeEntityList, self).__init__()
                self.hit_successfully = False
                self.index_called = None

            def _weight_function(self, index):
                self.hit_successfully = True
                self.index_called = index
                return 999.9

        test_object = FakeEntityList()
        ent1 = Entity("1")
        test_object.append(ent1)

        ent2 = Entity("2")
        test_object.append(ent2)

        returned_value = test_object.get_weight_for_entity(ent2)
        self.assertTrue(test_object.hit_successfully,
                        "Should have called the _weight_function() method "
                        "but didn't")
        self.assertEqual(2, test_object.index_called,
                         "Should have called the _weight_function() method "
                         "with index 2 but didn't")
        self.assertEqual(999.9, returned_value,
                         "Should return the value from the function for a"
                         "contained Entity")

    def test_weight_for_entity_returns_list_weight_for_contained_entity(self):
        """Check that an EntityList returns the list weight when asked for the
        weight for a Entity that is in its list of Entities"""

        test_object = EntityList()
        test_object.weight = 1234.567

        ent1 = Entity("1")
        test_object.append(ent1)

        ent2 = Entity("2")
        test_object.append(ent2)

        returned_value = test_object.get_weight_for_entity(ent2)
        self.assertEqual(1234.567, returned_value,
                         "Should return the list weight for a"
                         "contained Entity")

    def test_exponential_list_calculates_proper_fit(self):
        """Check that an ExponentialEntityList object calculates the
        fit parameters that we expect. Values that we use to test against
        were derived empirically running on a MacBook Pro."""

        target_scores = [10.6, 8.2, 10.7, 7.1, 4.2, 2.0, 3.3, 2.1]

        test_list_name = "Test_List_1"
        test_object = ExponentialEntityList()
        test_object.name = test_list_name

        x = 0
        sum_of_scores = 0.0
        for target_score in target_scores:
            ent = Entity("{}".format(x + 1))
            ent.score = target_score
            sum_of_scores += target_score
            test_object.append(ent)
            x = x + 1
        test_object.weight = sqrt(sum_of_scores / len(target_scores))

        test_object._fit_curve_to_entity_scores()
        params = test_object.fit_parameters
        self.assertAlmostEqual(3.425330010849388, params[0], 7,
                               "Expected value not found in fit "
                               "parameters slot 0")
        self.assertAlmostEqual(0.03952321646536448, params[1], 8,
                               "Expected value not found in fit "
                               "parameters slot 1")
        # the value in slot 2 is zero to all intents and purposes
        # differences in chip architecture make this a difficult value
        # to test so we compromise
        self.assertAlmostEqual(0.0, params[2], 14,
                               "Expected value not found in fit "
                               "parameters slot 2")

        # check that we get the right ratio to correct the distributed weights
        self.assertAlmostEqual(1.172902698170773, test_object.ratio, 9)

    @patch("entitylist.logger.warning")
    @patch("entitylist.curve_fit")
    def test_exponential_list_fails_gracefully_if_no_fit(self,
                                                         mock_curve_fit,
                                                         mock_logger):
        """Check that an ExponentialEntityList object falls back to a
        pre-defined set of default (near unranked) parameters if the
        curve_fit call fails in the library code"""

        rte_text = 'Optimal parameters not found: The maximum number of ' \
                   'function evaluations is exceeded.'
        mock_curve_fit.side_effect = RuntimeError(rte_text)

        test_list_name = "Test_List_1"
        test_object = ExponentialEntityList()
        test_object.name = test_list_name

        ent4 = Entity("4")
        ent4.score = 4
        test_object.append(ent4)

        ent3 = Entity("3")
        ent3.score = 3
        test_object.append(ent3)

        ent2 = Entity("2")
        ent2.score = 2
        test_object.append(ent2)

        ent1 = Entity("1")
        ent1.score = 1
        test_object.append(ent1)

        # In the real code, the list weight will have been calculated
        # before we call the _fit_curve_to_entity_scores() method
        fake_weight = uniform(3.0, 4.0)
        test_object.weight = fake_weight

        test_object._fit_curve_to_entity_scores()
        params = test_object.fit_parameters
        expected_params = [0, 0, 0]
        self.assertEqual(expected_params, params,
                         "Unexpected parameters found")

        # check that the logger was called with a warning
        expected_warning = "An error occured when trying to fit a " \
                           "function to distribute weights for " \
                           "list {}. The error was '{}'".format(test_list_name,
                                                                rte_text)
        mock_logger.assert_called_with(expected_warning)

        # check the weights values.
        expected_weights = []
        entity_count = len(test_object)
        base = test_object.weight + (
                    (FAILED_RANKED_LIST_DESCENT_STEP * entity_count) / 2.0)
        for x in range(entity_count):
            expected_weights.append(
                base - (x * FAILED_RANKED_LIST_DESCENT_STEP))
        distributed_average = np.average(expected_weights)
        # NOTE - we occasionally get floating point representation problems
        # if we check to 8 decimal places
        self.assertAlmostEqual(fake_weight, distributed_average, 7)
        self.assertEqual(expected_weights, test_object.weights_list,
                         "Unexpected distributed weights")

        # check the ratio
        self.assertEqual(1, test_object.ratio, "Ratio should be 1")

    def test_ranked_list_names_self_correctly(self):
        """Check that a ranked list correctly reports itself using the string
        naming convention"""
        from random import randint

        test_object = EntityList()
        test_object.is_ranked = True

        list_count = randint(1, 20)
        for x in range(0, list_count):
            entity = Entity(str(x))
            test_object.append(entity)

        self.assertEqual(str(list_count) + "r", test_object.code_string(),
                         "Got an unexpected code_string")

    def test_unranked_list_names_self_correctly(self):
        """Check that an unranked list correctly reports itself using the
        string naming convention"""
        from random import randint

        test_object = EntityList()
        test_object.is_ranked = False

        list_count = randint(1, 20)
        for x in range(0, list_count):
            entity = Entity(str(x))
            test_object.append(entity)

        self.assertEqual(str(list_count) + "u", test_object.code_string(),
                         "Got an unexpected code_string")

    def test_unfitted_exponential_list_returns_weight_one(self):
        """Check that an unfitted ExponentialEntityList returns a weight
        of one for each index slot"""
        test_object = ExponentialEntityList()

        self.assertEqual(1, test_object._weight_function(1),
                         'Should get weight 1')

    def test_entitylist_has_initial_base_score_mean_zero(self):
        """Check that an EntityList object has a base_score_mean of 0 by
        default."""
        test_object = EntityList()
        self.assertEqual(0.0, test_object.base_score_mean,
                         "Default EntityList base_score_mean should be zero")

    def test_entitylist_has_initial_base_score_stdev_one(self):
        """Check that an EntityList object has a base_score_stdev of 1 by
        default."""
        test_object = EntityList()
        self.assertEqual(1.0, test_object.base_score_stdev,
                         "Default EntityList base_score_stdev should be one")

    def test_adjusted_weight(self):
        """Check that the adjusted_weight method does the right thing"""
        initial = uniform(10, 99)
        mean = uniform(1, 10)
        stdev = uniform(0.1, 2)
        transformed_score = uniform(-10, -5)
        scaled_score = uniform(100, 101)

        transformer = MagicMock()
        transformer.transform = MagicMock(return_value = transformed_score)

        scaler = MagicMock()
        scaler.scale = MagicMock(return_value = scaled_score)

        expected_result = scaled_score
        self.assertEqual(expected_result,
                         EntityList.adjusted_weight(initial, mean, stdev, transformer,
                                         scaler),
                         'adjusted_weight')

        # check that the mocks were called with the expected arguments
        transformer.transform.assert_called_once_with(initial, mean)
        scaler.scale.assert_called_once_with(transformed_score, stdev)

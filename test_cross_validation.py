import itertools
from unittest import TestCase

import mock
from mock import call, Mock

from cross_validation import CrossValidation, POST_ITERATION_CALLBACK
from entity import Entity
from entitylist import EntityList


class TestCrossValidation(TestCase):

    def test_stop_on_max_iterations(self):
        """If the EntityLists never get their delta down below the threshold
        then we are not converging so we continue to process. Eventually we
        need to stop after the specified number of iterations
        """
        __MAX_ITERATIONS = 10
        __THRESHOLD = 0.1
        __SUPRA_THRESHOLD = 2.0
        __EXPECTED_ITERATIONS = __MAX_ITERATIONS

        # Create two mock entities
        ent1 = mock.create_autospec(Entity)
        ent2 = mock.create_autospec(Entity)

        # Create a mock EntityList. Set the calculate_new_weight attribute
        # to be another mock, then set a side_effect to fake out successive
        # return values. All of them are above threshold values
        entity_list1 = mock.create_autospec(EntityList)
        entity_list1.calculate_new_weight = Mock()
        entity_list1.calculate_new_weight.side_effect = list(
            itertools.repeat(__SUPRA_THRESHOLD, __MAX_ITERATIONS))
        # Repeat for a second mock EntityList
        entity_list2 = mock.create_autospec(EntityList)
        entity_list2.calculate_new_weight = Mock()
        entity_list2.calculate_new_weight.side_effect = list(
            itertools.repeat(__SUPRA_THRESHOLD, __MAX_ITERATIONS))

        entities = [ent1, ent2]
        entity_lists = [entity_list1, entity_list2]

        tested_object = CrossValidation(entities, entity_lists, __THRESHOLD,
                                        __MAX_ITERATIONS)

        tested_object.run_analysis()

        expected_calls = list(itertools.repeat(call(), __MAX_ITERATIONS))
        ent1.calculate_new_score.assert_has_calls(expected_calls)
        self.assertEqual(__EXPECTED_ITERATIONS,
                         ent1.calculate_new_score.call_count)
        ent2.calculate_new_score.assert_has_calls(expected_calls)
        entity_list1.calculate_new_weight.assert_has_calls(expected_calls)
        entity_list2.calculate_new_weight.assert_has_calls(expected_calls)

    def test_one_list_never_hits_delta_threshold(self):
        """Check that the scoring continues for __MAX_ITERATIONS when one list
        fails to converge below __THRESHOLD.
        (i.e. all but one list are below the threshold but one remains
        stubbornly above and hence we continue to go around the loop."""
        __MAX_ITERATIONS = 10
        __THRESHOLD = 0.1
        __SUPRA_THRESHOLD = 2.0
        __SUB_THRESHOLD = 0.0001

        # Create two mock entities
        ent1 = mock.create_autospec(Entity)
        ent2 = mock.create_autospec(Entity)

        # Create a mock EntityList. Set the calculate_new_weight attribute
        # to be another mock, then set a side_effect to fake out successive
        # return values. All of them are above threshold values
        entity_list1 = mock.create_autospec(EntityList)
        entity_list1.calculate_new_weight = Mock()
        entity_list1.calculate_new_weight.side_effect = list(
            itertools.repeat(__SUPRA_THRESHOLD, __MAX_ITERATIONS))
        # Repeat for a second mock EntityList
        # NOTE - the second list returns __SUB_THRESHOLD
        entity_list2 = mock.create_autospec(EntityList)
        entity_list2.calculate_new_weight = Mock()
        entity_list2.calculate_new_weight.side_effect = list(
            itertools.repeat(__SUB_THRESHOLD, __MAX_ITERATIONS))

        entities = [ent1, ent2]
        entity_lists = [entity_list1, entity_list2]

        tested_object = CrossValidation(entities, entity_lists, __THRESHOLD,
                                        __MAX_ITERATIONS)

        tested_object.run_analysis()

        expected_calls = list(itertools.repeat(call(), __MAX_ITERATIONS))
        ent1.calculate_new_score.assert_has_calls(expected_calls)
        ent2.calculate_new_score.assert_has_calls(expected_calls)
        entity_list1.calculate_new_weight.assert_has_calls(expected_calls)
        entity_list2.calculate_new_weight.assert_has_calls(expected_calls)

    def test_lists_fall_below_delta_threshold(self):
        """Check that the scoring stops as soon as all lists drop below the
        delta threshold."""
        __MAX_ITERATIONS = 10
        __THRESHOLD = 0.1
        __SUPRA_THRESHOLD = 2.0
        __SUB_THRESHOLD = 0.0001
        __EXPECTED_ITERATIONS = 5

        # Create two mock entities
        ent1 = mock.create_autospec(Entity)
        ent2 = mock.create_autospec(Entity)

        # Create a mock EntityList. Set the calculate_new_weight attribute
        # to be another mock, then set a side_effect to fake out successive
        # return values. The first one is above threshold values and then we
        # drop below threshold for subsequent calls.
        entity_list1 = mock.create_autospec(EntityList)
        entity_list1.calculate_new_weight = Mock()
        entity_list1.calculate_new_weight.side_effect = [__SUPRA_THRESHOLD,
                                                         __SUB_THRESHOLD,
                                                         __SUB_THRESHOLD,
                                                         __SUB_THRESHOLD,
                                                         __SUB_THRESHOLD,
                                                         __SUB_THRESHOLD,
                                                         __SUB_THRESHOLD,
                                                         __SUB_THRESHOLD]
        # Repeat for a second mock EntityList
        # NOTE - the second list returns __SUPRA_THRESHOLD for four iterations
        #  and then reports __SUB_THRESHOLD after that
        entity_list2 = mock.create_autospec(EntityList)
        entity_list2.calculate_new_weight = Mock()
        entity_list2.calculate_new_weight.side_effect = [__SUPRA_THRESHOLD,
                                                         __SUPRA_THRESHOLD,
                                                         __SUPRA_THRESHOLD,
                                                         __SUPRA_THRESHOLD,
                                                         __SUB_THRESHOLD,
                                                         __SUB_THRESHOLD,
                                                         __SUB_THRESHOLD,
                                                         __SUB_THRESHOLD]

        entities = [ent1, ent2]
        entity_lists = [entity_list1, entity_list2]

        tested_object = CrossValidation(entities, entity_lists, __THRESHOLD,
                                        __MAX_ITERATIONS)

        tested_object.run_analysis()

        expected_calls = list(itertools.repeat(call(), __EXPECTED_ITERATIONS))
        ent1.calculate_new_score.assert_has_calls(expected_calls)
        self.assertEqual(__EXPECTED_ITERATIONS,
                         ent1.calculate_new_score.call_count)
        ent2.calculate_new_score.assert_has_calls(expected_calls)
        self.assertEqual(__EXPECTED_ITERATIONS,
                         ent2.calculate_new_score.call_count)
        entity_list1.calculate_new_weight.assert_has_calls(expected_calls)
        self.assertEqual(__EXPECTED_ITERATIONS,
                         entity_list1.calculate_new_weight.call_count)
        entity_list2.calculate_new_weight.assert_has_calls(expected_calls)
        self.assertEqual(__EXPECTED_ITERATIONS,
                         entity_list2.calculate_new_weight.call_count)

    def test_delta_threshold_check_handles_negatives(self):
        """Check that the scoring continues if a list has a large negative
        delta - we are interested in abs() values"""
        __MAX_ITERATIONS = 10
        __THRESHOLD = 0.1
        __SUPRA_THRESHOLD = 2.0
        __SUPRA_NEGATIVE_THRESHOLD = -2.0
        __SUB_THRESHOLD = 0.0001
        __SUB_NEGATIVE_THRESHOLD = -0.0001
        __EXPECTED_ITERATIONS = 6

        # Create two mock entities
        ent1 = mock.create_autospec(Entity)
        ent2 = mock.create_autospec(Entity)

        # Create a mock EntityList. Set the calculate_new_weight attribute
        # to be another mock, then set a side_effect to fake out successive
        # return values. The first one is above threshold values and then we
        # drop below threshold for subsequent calls.
        entity_list1 = mock.create_autospec(EntityList)
        entity_list1.calculate_new_weight = Mock()
        entity_list1.calculate_new_weight.side_effect = [__SUPRA_THRESHOLD,
                                                         __SUB_THRESHOLD,
                                                         __SUB_THRESHOLD,
                                                         __SUB_THRESHOLD,
                                                         __SUB_THRESHOLD,
                                                         __SUB_THRESHOLD,
                                                         __SUB_THRESHOLD,
                                                         __SUB_THRESHOLD]
        # Repeat for a second mock EntityList
        # NOTE - the second list returns __SUPRA_NEGATIVE_THRESHOLD for five
        # iterations and then reports __SUB_NEGATIVE_THRESHOLD after that
        entity_list2 = mock.create_autospec(EntityList)
        entity_list2.calculate_new_weight = Mock()
        entity_list2.calculate_new_weight.side_effect = [
            __SUPRA_NEGATIVE_THRESHOLD,
            __SUPRA_NEGATIVE_THRESHOLD,
            __SUPRA_NEGATIVE_THRESHOLD,
            __SUPRA_NEGATIVE_THRESHOLD,
            __SUPRA_NEGATIVE_THRESHOLD,
            __SUB_NEGATIVE_THRESHOLD,
            __SUB_NEGATIVE_THRESHOLD,
            __SUB_NEGATIVE_THRESHOLD
        ]

        entities = [ent1, ent2]
        entity_lists = [entity_list1, entity_list2]

        tested_object = CrossValidation(entities, entity_lists, __THRESHOLD,
                                        __MAX_ITERATIONS)

        tested_object.run_analysis()

        expected_calls = list(itertools.repeat(call(), __EXPECTED_ITERATIONS))
        ent1.calculate_new_score.assert_has_calls(expected_calls)
        self.assertEqual(__EXPECTED_ITERATIONS,
                         ent1.calculate_new_score.call_count)
        ent2.calculate_new_score.assert_has_calls(expected_calls)
        self.assertEqual(__EXPECTED_ITERATIONS,
                         ent2.calculate_new_score.call_count)
        entity_list1.calculate_new_weight.assert_has_calls(expected_calls)
        self.assertEqual(__EXPECTED_ITERATIONS,
                         entity_list1.calculate_new_weight.call_count)
        entity_list2.calculate_new_weight.assert_has_calls(expected_calls)
        self.assertEqual(__EXPECTED_ITERATIONS,
                         entity_list2.calculate_new_weight.call_count)

    def test_code_string_reports_correctly(self):
        """Check that a CrossValidation analysis object collects and reports
        the set of EntityList code strings correctly"""
        # Create two mock entities
        ent1 = mock.create_autospec(Entity)
        ent2 = mock.create_autospec(Entity)

        # Create a mock EntityList. Set the code_string attribute
        # to be another mock, then set a side_effect to fake out a return
        # value. Set a fake category
        entity_list1 = mock.create_autospec(EntityList)
        entity_list1.code_string = Mock()
        entity_list1.code_string.side_effect = ["261u"]
        entity_list1.category = "category1"

        # Repeat for a second mock EntityList using the same category
        entity_list2 = mock.create_autospec(EntityList)
        entity_list2.code_string = Mock()
        entity_list2.code_string.side_effect = ["35r"]
        entity_list2.category = "category1"

        # Repeat for a third mock EntityList using a different category
        entity_list3 = mock.create_autospec(EntityList)
        entity_list3.code_string = Mock()
        entity_list3.code_string.side_effect = ["299r"]
        entity_list3.category = "category2"

        entities = [ent1, ent2]
        entity_lists = [entity_list1, entity_list2, entity_list3]

        tested_object = CrossValidation(entities, entity_lists, 0.5, 99)
        self.assertEqual("261u.35r|299r", tested_object.code_string(),
                         "Unexpected code string from CrossValidation object")

    def test_summary_data(self):
        """Check that the CrossValidation object does the right thing when
        asked to calculate the summary data"""

        # make a couple of Entities
        ent1 = Entity("1")
        ent1.score = 1
        ent2 = Entity("2")
        ent2.score = 2
        ent3 = Entity("3")
        ent3.score = 3

        entities = [ent1, ent2, ent3]
        entity_lists = ["fool the assertions"]
        test_object = CrossValidation(entities, entity_lists, 0.001, 999)

        returned_details = test_object.summary_data()
        self.assertAlmostEqual(2.0, returned_details[0], 14,
                               "Unexpected average")
        self.assertAlmostEqual(0.816496580927726, returned_details[1], 14,
                               "Unexpected average")

    def test_callback_types_are_as_expected(self):
        """Check that the callbacks in a new CrossValidation object only
        contain expected keys and that the list of callbacks for each type is
        empty by default"""

        expected_type_count = 1
        expected_types = [POST_ITERATION_CALLBACK]

        test_object = CrossValidation(['fake'], ['fake'], 1, 1)
        self.assertEqual(expected_type_count, len(test_object.callbacks))
        for type in expected_types:
            self.assertTrue(type in test_object.callbacks)
        for type in test_object.callbacks:
            self.assertTrue(type in expected_types)
            self.assertFalse(test_object.callbacks[type])

    def test_can_set_callback(self):
        """Check that we can stuff a callback object into the relevant slot
        in our CrossValidation object"""
        test_object = CrossValidation(['fake'], ['fake'], 1, 1)

        fake_callback_object = mock.MagicMock()

        test_object.register_callback(POST_ITERATION_CALLBACK,
                                      fake_callback_object)
        post_iteration_callbacks = test_object.callbacks[POST_ITERATION_CALLBACK]
        self.assertTrue(post_iteration_callbacks)
        self.assertTrue(fake_callback_object in post_iteration_callbacks)

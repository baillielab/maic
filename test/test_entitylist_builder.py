import unittest

from mock import patch

from maic.entitylist_builder import EntityListBuilder
from maic.errors import WarnValueError, KillValueError
from maic.entitylist import EntityList, KnnEntityList, SvrEntityList, \
    PolynomialEntityList, ExponentialEntityList


class TestEntityListBuilder(unittest.TestCase):
    ZERO_COL_STRING = ""
    ONE_COL_STRING = "category"
    TWO_COL_STRING = "category\tname"
    THREE_COL_STRING = "category\tname\tranked"
    FOUR_COL_STRING = "category\tname\tranked\tignored"
    VALID_STRING = "category\tname\tranked\tignored\ta\tb\tc"
    VALID_STRING_REPEATS = "category\tname\tnot_ranked\tignored\ta\ta\ta"
    VALID_STRING_BLANK_COL = "category\tname\tranked\tignored\ta\t\tb\tc"
    VALID_STRING_TRAILING_BLANK_COLS = \
        "category\tname\tranked\tignored\ta\tb\tc\t \t \t\t"
    VALID_LONG_STRING = "c\tn\tranked\ti\t1\t2\t3\t4\t5\t6\t7\t8\t9\t10\t11" \
                        "\t12\t13\t14\t15\t16\t17\t18\t19\t20\t21\t22\t23" \
                        "\t24\t25\t26\t27\t28\t29\t30"
    VALID_LONG_STRING_WITH_GAPS = "c\tn\tranked\ti\t1\t2\t\t\t5\t6\t7\t8\t9" \
                                  "\t10\t11\t12\t13\t14\t15\t16\t17\t18\t19" \
                                  "\t20\t21\t22\t23\t24\t25\t26\t27\t28\t29" \
                                  "\t30"

    def test_zero_col_string_throws_exception(self):
        """Test that an empty string causes a WarnValueError Exception"""
        test_object = EntityListBuilder('none')
        with self.assertRaises(WarnValueError) as context:
            test_object.build_list_from_string(self.ZERO_COL_STRING)

        self.assertTrue('Insufficient columns to create an EntityList' in
                        context.exception.args)

    def test_one_col_string_throws_exception(self):
        """Test that a one column string causes a WarnValueError Exception"""
        test_object = EntityListBuilder('none')
        with self.assertRaises(WarnValueError) as context:
            test_object.build_list_from_string(self.ONE_COL_STRING)

        self.assertTrue('Insufficient columns to create an EntityList' in
                        context.exception.args)

    def test_two_col_string_throws_exception(self):
        """Test that a two column string causes a WarnValueError Exception"""
        test_object = EntityListBuilder('none')
        with self.assertRaises(WarnValueError) as context:
            test_object.build_list_from_string(self.TWO_COL_STRING)

        self.assertTrue('Insufficient columns to create an EntityList' in
                        context.exception.args)

    def test_three_col_string_throws_exception(self):
        """Test that a three column string causes a WarnValueError Exception"""
        test_object = EntityListBuilder('none')
        with self.assertRaises(WarnValueError) as context:
            test_object.build_list_from_string(self.THREE_COL_STRING)

        self.assertTrue('Insufficient columns to create an EntityList' in
                        context.exception.args)

    def test_four_col_string_does_not_throw_exception(self):
        """
        Test that a four column string does not cause a WarnValueError
        Exception
        """
        test_object = EntityListBuilder('none')
        try:
            entitylist = test_object.build_list_from_string(
                self.FOUR_COL_STRING)
        except WarnValueError:
            self.fail("Should not have got here because four columns is "
                      "sufficient")
        self.assertTrue(len(entitylist) == 0)
        self.assertTrue(entitylist.is_ranked)

    def test_valid_string_builds_acceptable_list(self):
        """
        Test that a valid string results in a list of the correct type
        with the expected number of entities in it
        """
        test_object = EntityListBuilder('none')
        try:
            entitylist = test_object.build_list_from_string(
                self.VALID_STRING)
        except WarnValueError:
            self.fail("Should not have got here because string is valid")
        self.assertTrue(len(entitylist) == 3,
                        "Expected list to have 3 entries")
        self.assertTrue(entitylist.is_ranked,
                        "Expected list to be ranked")

    def test_builder_strips_repeats(self):
        """
        Test that a valid string with repeats results in the correct
        number of entities being included in the list
        """
        test_object = EntityListBuilder('none')
        try:
            entitylist = test_object.build_list_from_string(
                self.VALID_STRING_REPEATS)
        except WarnValueError:
            self.fail("Should not have got here because string is valid")
        self.assertTrue(len(entitylist) == 1,
                        "Expected list to have 1 entry")
        self.assertFalse(entitylist.is_ranked,
                         "Expected list NOT to be ranked")

    def test_builder_detects_clashes_of_list_name(self):
        """
        Test that asking an EntityListBuilder to create two lists with the
        same name raises a KillValueExceptionException
        """
        test_object = EntityListBuilder('none')
        try:
            entitylist = test_object.build_list_from_string(
                self.VALID_STRING_REPEATS)
        except WarnValueError:
            self.fail("Should not have got here because string is valid")
        self.assertTrue(len(entitylist) == 1,
                        "Expected list to have 1 entry")
        self.assertFalse(entitylist.is_ranked,
                         "Expected list NOT to be ranked")
        with self.assertRaises(KillValueError) as context:
            test_object.build_list_from_string(self.VALID_STRING_REPEATS)
        self.assertTrue(
            'List with that name already exists' in
            context.exception.args)

    @patch('logging.Logger.warning')
    def test_string_with_blanks_builds_acceptable_list_and_warns(self,
                                                                 mock_logger):
        """
        Test that a string that contains blank columns results in a list of
        the correct type with the expected number of entities in it
        """
        test_object = EntityListBuilder('none')
        # noinspection PyBroadException
        try:
            entitylist = test_object.build_list_from_string(
                self.VALID_STRING_BLANK_COL)
        except WarnValueError:
            self.fail("Should not have got here because string is valid")
        except BaseException:
            self.fail("Should not get here either")
        self.assertEqual(3, len(entitylist),
                         "Expected list to have 3 entries")
        self.assertTrue(entitylist.is_ranked,
                        "Expected list to be ranked")
        mock_logger.assert_called_with("Found an empty column - "
                                       "column 6 in list 'name'")

    @patch('logging.Logger.warning')
    def test_string_with_trailing_blanks_builds_no_warn(self,mock_logger):
        """
        Test that a string that contains blank columns results in a list of
        the correct type with the expected number of entities in it
        """
        test_object = EntityListBuilder('none')
        # noinspection PyBroadException
        try:
            entitylist = test_object.build_list_from_string(
                self.VALID_STRING_TRAILING_BLANK_COLS)
        except WarnValueError:
            self.fail("Should not have got here because string is valid")
        except BaseException:
            self.fail("Should not get here either")
        self.assertEqual(3, len(entitylist),
                         "Expected list to have 3 entries")
        self.assertTrue(entitylist.is_ranked,
                        "Expected list to be ranked")
        mock_logger.assert_not_called()

    def test_appropriate_entitylist_none_arguments(self):
        """
        Test that None arguments are unacceptable
        :return:
        """
        test_object = EntityListBuilder(None)
        with self.assertRaises(AssertionError):
            test_object.get_appropriate_entitylist(None)

    def test_unranked_is_always_plain_entity_list(self):
        """If the list is unranked, we always get a plain EntityList"""
        for option in ['knn', 'none', 'polynomial', 'exponential', 'svr',
                       'fake']:
            test_object = EntityListBuilder(option)
            entity_list = test_object.get_appropriate_entitylist(False)
            self.assertIsInstance(entity_list, EntityList)

    @patch('logging.Logger.warning')
    def test_ranked_gives_correct_entity_list_subclass(self, mock_logger):
        """Check that we get the correct EntityList subclass if we have
         a ranked list"""
        test_object = EntityListBuilder('knn')
        entity_list = test_object.get_appropriate_entitylist(True)
        self.assertIsInstance(entity_list, KnnEntityList)

        test_object = EntityListBuilder('none')
        entity_list = test_object.get_appropriate_entitylist(True)
        self.assertIsInstance(entity_list, EntityList)

        test_object = EntityListBuilder('polynomial')
        entity_list = test_object.get_appropriate_entitylist(True)
        self.assertIsInstance(entity_list, PolynomialEntityList)

        test_object = EntityListBuilder('exponential')
        entity_list = test_object.get_appropriate_entitylist(True)
        self.assertIsInstance(entity_list, ExponentialEntityList)

        test_object = EntityListBuilder('svr')
        entity_list = test_object.get_appropriate_entitylist(True)
        self.assertIsInstance(entity_list, SvrEntityList)

        test_object = EntityListBuilder('fake')
        entity_list = test_object.get_appropriate_entitylist(True)
        self.assertIsInstance(entity_list, EntityList)
        mock_logger.assert_called_with("Unrecognised EntityList Type ("
                                       "'fake'). Returning an unranked "
                                       "EntityList.")

    def test_list_builder_limits_via_from_string_arg_no_arg(self):
        """Check that we get the right length list when we do not supply a
         limit argument to the build_list_from_string() function"""
        test_object = EntityListBuilder('none')
        entity_list = test_object.build_list_from_string(
            self.VALID_LONG_STRING)
        self.assertEqual(30, len(entity_list), "Should be 30 entries")

    @patch('logging.Logger.warning')
    def test_list_builder_limits_via_from_string_arg_lower_arg(self,
                                                               mock_logger):
        """Check that we can limit the length of the returned list by passing
        in a parameter to the build_list_from_string() function"""
        test_object = EntityListBuilder('none')
        entity_list = test_object.build_list_from_string(
            self.VALID_LONG_STRING, 19)
        self.assertEqual(19, len(entity_list), "Should be 19 entries")
        mock_logger.assert_called_with("Some data in list 'n' was ignored due "
                                       "to a limit on list lengths (19). Up "
                                       "to 11 columns were skipped.")

    def test_list_builder_limits_via_from_string_arg_higher_arg(self):
        """Check that we a limit argument greater than the number of items in
        the supplied string has no effect on returned list length from the
        build_list_from_string() function"""
        test_object = EntityListBuilder('none')
        entity_list = test_object.build_list_from_string(
            self.VALID_LONG_STRING, 999)
        self.assertEqual(30, len(entity_list), "Should be 30 entries")

    @patch('logging.Logger.warning')
    def test_list_builder_limits_via_from_string_allows_for_gaps(self,
                                                                 mock_logger):
        """Check that we can limit the length of the returned list by passing
        in a parameter to the build_list_from_string() function and this
        works even if there are gaps in the columns supplied"""
        test_object = EntityListBuilder('none')
        entity_list = test_object.build_list_from_string(
            self.VALID_LONG_STRING_WITH_GAPS, 23)
        self.assertEqual(23, len(entity_list), "Should be 23 entries")
        mock_logger.assert_called_with("Some data in list 'n' was ignored due "
                                       "to a limit on list lengths (23). Up "
                                       "to 5 columns were skipped.")

    @patch('logging.Logger.warning')
    def test_list_builder_limits_via_constructor(self, mock_logger):
        """Check that we can limit the size of the list returned by
        setting the value in the EntityListBuilder constructor"""
        test_object = EntityListBuilder('none', 13)
        entity_list = test_object.build_list_from_string(
            self.VALID_LONG_STRING)
        self.assertEqual(13, len(entity_list), "Should be 13 entries")
        mock_logger.assert_called_with("Some data in list 'n' was ignored due "
                                       "to a limit on list lengths (13). Up "
                                       "to 17 columns were skipped.")

    @patch('logging.Logger.warning')
    def test_list_builder_fnctn_arg_overrides_constructor_limit(self,
                                                                mock_logger):
        """Check that the value we supply as an argument to the list_builder
         from string function overrides the value we pass in to the constructor
         """
        test_object = EntityListBuilder('none', 13)
        entity_list = test_object.build_list_from_string(
            self.VALID_LONG_STRING, 18)
        self.assertEqual(18, len(entity_list), "Should be 18 entries")
        mock_logger.assert_called_with("Some data in list 'n' was ignored due "
                                       "to a limit on list lengths (18). Up "
                                       "to 12 columns were skipped.")

    def test_same_object_retrieved_for_same_name(self):
        """
        Test that we get the same object from the get_or_create_entity()
        function when we give the same name.
        """
        test_object = EntityListBuilder('none')
        entity_a = test_object.get_or_create_entity("A")
        entity_b = test_object.get_or_create_entity("A")
        self.assertTrue(entity_a == entity_b)

    def test_only_one_object_created_for_single_name(self):
        """
        Test that only one object is created by the get_or_create_entity()
        function when we give the same name multiple times.
        """
        test_object = EntityListBuilder('none')
        test_object.get_or_create_entity("A")
        test_object.get_or_create_entity("A")
        test_object.get_or_create_entity("A")
        test_object.get_or_create_entity("A")
        count = len(test_object.entities())
        self.assertEqual(1, count, "Should be a single object in the list "
                                   "of entities")

    def test_different_object_retrieved_for_case_different_name(self):
        """
        Test that we get a different object from the get_or_create_entity()
        function when we give names differing in case.
        """
        test_object = EntityListBuilder('none')
        entity_upper_a = test_object.get_or_create_entity("A")
        entity_lower_a = test_object.get_or_create_entity("a")
        count = len(test_object.entities())
        self.assertEqual(2, count, "Should be 2 objects in the list of "
                                   "entities")
        self.assertFalse(entity_upper_a == entity_lower_a,
                         "Should be different objects")
        self.assertTrue(entity_lower_a in test_object.entities())
        self.assertTrue(entity_upper_a in test_object.entities())

    def test_default_entities_is_empty(self):
        """Test that the default set of entities is empty"""
        test_object = EntityListBuilder('none')
        self.assertEqual(0, len(test_object.entities()))

    def test_list_builders_are_independent(self):
        """Test that adding to one List Builder does not affect another one"""
        test_object1 = EntityListBuilder('none')
        test_object2 = EntityListBuilder('none')
        test_object1.get_or_create_entity("A")
        self.assertEqual(1, len(test_object1.entities()))
        self.assertEqual(0, len(test_object2.entities()))
        test_object2.get_or_create_entity("A")
        self.assertEqual(1, len(test_object1.entities()))
        self.assertEqual(1, len(test_object2.entities()))


if __name__ == '__main__':
    unittest.main()

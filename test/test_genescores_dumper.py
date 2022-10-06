from unittest import TestCase, main

import mock

from maic.constants import T_METHOD_NONE
from maic.cross_validation import CrossValidation
from maic.entity import Entity
from maic.entitylist import EntityList
from genescores_dumper import GeneScoresDumper, IterationAwareGeneScoresDumper


class TestGeneScoresDumper(TestCase):

    def test_lists_are_ordered_correctly(self):
        """Check that the code correctly orders contained EntityLists
        by category and then by name"""

        # Create three mock EntityLists
        elist1 = mock.create_autospec(EntityList)
        elist1.category = 'category1'
        elist1.name = 'Z-name'
        elist2 = mock.create_autospec(EntityList)
        elist2.category = 'category2'
        elist2.name = 'list 2'
        elist3 = mock.create_autospec(EntityList)
        elist3.category = 'category1'
        elist3.name = 'list 3'

        # Create a mock CrossValidation object
        cross_val = mock.create_autospec(CrossValidation)
        cross_val.entity_lists = [elist1, elist2, elist3]
        cross_val.entities = []

        test_object = GeneScoresDumper(cross_val)
        lists = test_object.lists_in_category_order()

        expected = [elist3, elist1, elist2]
        self.assertListEqual(expected, lists,
                             ("Unexpected difference in list returned - "
                              "%s vs %s" % (expected, lists)))

    @mock.patch('io.open')
    def test_dump(self, mock_open):
        """Test the logic of the GeneScoresDump export"""
        handle = mock.MagicMock()
        fake_output_directory = '/local/directory'

        # Create three mock EntityLists
        elist1 = mock.create_autospec(EntityList)
        elist1.category = 'category1'
        elist1.name = 'elist1'
        elist2 = mock.create_autospec(EntityList)
        elist2.category = 'category1'
        elist2.name = 'elist2'
        elist3 = mock.create_autospec(EntityList)
        elist3.category = 'category2'
        elist3.name = 'elist3'

        # put them in a list and make a function that we can use to
        # override the standard GeneScoresDumper lists_in_category_order()
        list_of_lists = [elist1, elist2, elist3]

        def mock_list_func():
            return list_of_lists

        # Create two mock entities
        ent1 = mock.create_autospec(Entity)
        ent1.name = 'GAPDH'
        # ent1.transformed_score = 9999
        trans_score_list1 = mock.MagicMock(side_effect=[9999])
        ent1.transformed_score = trans_score_list1
        score_from_list1 = mock.MagicMock(side_effect=[0.0, 1.1, 2.2])
        ent1.score_from_list = score_from_list1
        ent2 = mock.create_autospec(Entity)
        ent2.name = 'TGFB3'
        # ent2.transformed_score = 8888
        trans_score_list2 = mock.MagicMock(side_effect=[8888])
        ent2.transformed_score = trans_score_list2
        score_from_list2 = mock.MagicMock(side_effect=[99.04, 10.0, 0])
        ent2.score_from_list = score_from_list2

        # put them in a list and make a function that we can use to
        # override the standard GeneScoresDumper
        # entities_in_descending_score_order()
        list_of_entities = [ent1, ent2]

        def mock_entity_func(method):
            return list_of_entities

        # Create a mock CrossValidation object
        cross_val = mock.create_autospec(CrossValidation)

        # Then make a test object and override the lists functions to
        # return our fake list of lists and list of entities
        test_object = GeneScoresDumper(cross_val,
                                       output_folder=fake_output_directory)
        test_object.lists_in_category_order = mock_list_func
        test_object.entities_in_descending_score_order = mock_entity_func

        self.assertListEqual(list_of_lists,
                             test_object.lists_in_category_order())

        mock_open.return_value = handle

        # Do the dump() call
        test_object.dump()

        expected_score_calls = [mock.call(elist1), mock.call(elist2),
            mock.call(elist3)]
        score_from_list1.assert_has_calls(expected_score_calls)
        score_from_list2.assert_has_calls(expected_score_calls)

        expected_transformed_score_calls = [mock.call(method=T_METHOD_NONE)]
        trans_score_list1.assert_has_calls(expected_transformed_score_calls)
        trans_score_list2.assert_has_calls(expected_transformed_score_calls)

        expected_calls = [
            mock.call('gene\telist1\telist2\telist3\tmaic_score\n'),
            mock.call('GAPDH\t0.0\t1.1\t2.2\t9999\n'),
            mock.call('TGFB3\t99.04\t10.0\t0.0\t8888\n')]

        handle.writelines.assert_has_calls(expected_calls)

    def test_entity_sorting(self):
        """Test that the entities from the CrossValidation object are
        extracted and sorted into score descending order"""

        # Create three entity objects
        ent1 = mock.create_autospec(Entity)
        # ent1_transformed_score = 9.44
        trans_score_list1 = mock.MagicMock(side_effect=[9.44])
        ent1.transformed_score = trans_score_list1
        ent2 = mock.create_autospec(Entity)
        # ent2.transformed_score = 1.6
        trans_score_list2 = mock.MagicMock(side_effect=[1.6])
        ent2.transformed_score = trans_score_list2
        ent3 = mock.create_autospec(Entity)
        # ent3.transformed_score = 19.77
        trans_score_list3 = mock.MagicMock(side_effect=[19.77])
        ent3.transformed_score = trans_score_list3

        # Create a mock CrossValidation object
        cross_val = mock.create_autospec(CrossValidation)
        cross_val.entity_lists = []
        cross_val.entities = [ent1, ent2, ent3]

        test_object = GeneScoresDumper(cross_val)
        lists = test_object.entities_in_descending_score_order()

        expected = [ent3, ent1, ent2]
        self.assertListEqual(expected, lists,
                             ("Unexpected difference in list returned - "
                              "%s vs %s" % (expected, lists)))

    def test_build_filename_and_methodname_simple(self):
        """Check that we get the expected result if we call with no
        arguments"""
        fake_cv = mock.MagicMock()
        test_object = GeneScoresDumper(fake_cv)

        result = test_object.build_file_and_method_name()

        self.assertEqual("maic_raw", result.filename)
        self.assertEqual("no_transform", result.methodname)

    def test_build_filename_and_methodname_simple_iteration_aware(self):
        """Check that we get the expected result if we call with no
        arguments on an IterationAwareGeneScoresDumper"""
        fake_cv = mock.MagicMock()
        test_object = IterationAwareGeneScoresDumper(fake_cv)

        result = test_object.build_file_and_method_name()

        self.assertEqual("maic_raw-000", result.filename)
        self.assertEqual("no_transform", result.methodname)

    def test_build_filename_and_methodname_simple_iteration_aware_i7(self):
        """Check that we get the expected result if we call with no
        arguments on an IterationAwareGeneScoresDumper that has had the
        iteration number tweaked"""
        fake_cv = mock.MagicMock()
        test_object = IterationAwareGeneScoresDumper(fake_cv)
        test_object.iteration = 7

        result = test_object.build_file_and_method_name()

        self.assertEqual("maic_raw-007", result.filename)
        self.assertEqual("no_transform", result.methodname)


if __name__ == '__main__':
    main()

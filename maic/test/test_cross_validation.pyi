from maic.cross_validation import CrossValidation as CrossValidation, POST_ITERATION_CALLBACK as POST_ITERATION_CALLBACK
from maic.entity import Entity as Entity
from maic.entitylist import EntityList as EntityList
from unittest import TestCase

class TestCrossValidation(TestCase):
    def test_stop_on_max_iterations(self) -> None: ...
    def test_one_list_never_hits_delta_threshold(self) -> None: ...
    def test_lists_fall_below_delta_threshold(self) -> None: ...
    def test_delta_threshold_check_handles_negatives(self) -> None: ...
    def test_code_string_reports_correctly(self) -> None: ...
    def test_summary_data(self) -> None: ...
    def test_callback_types_are_as_expected(self) -> None: ...
    def test_can_set_callback(self) -> None: ...

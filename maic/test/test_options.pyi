from _typeshed import Incomplete
from maic.constants import T_METHOD_NONE as T_METHOD_NONE
from unittest import TestCase

EXPECTED_OPTION_ATTRIBUTE_KEYS: Incomplete
EXPECTED_OPTION_ATTRIBUTE_COUNT: Incomplete

class TestOptions(TestCase):
    def test_attribute_list_matches_expected(self) -> None: ...
    def test_default_filename(self) -> None: ...
    def test_filename_is_settable(self) -> None: ...
    def test_default_max_input_len(self) -> None: ...
    def test_default_random_source_len(self) -> None: ...
    def test_default_stability(self) -> None: ...
    def test_default_max_iterations(self) -> None: ...
    def test_default_logging_level_is_warn(self) -> None: ...
    def test_single_v_equals_log_level_warn(self) -> None: ...
    def test_can_set_info_log_level(self) -> None: ...
    def test_can_set_debug_log_level(self) -> None: ...
    def test_single_v_equals_log_level_warn_long(self) -> None: ...
    def test_can_set_info_log_level_long(self) -> None: ...
    def test_can_set_debug_log_level_long(self) -> None: ...
    def test_can_set_error_log_level(self) -> None: ...
    def test_can_set_critical_log_level(self) -> None: ...
    def test_can_set_error_log_level_long(self) -> None: ...
    def test_can_set_critical_log_level_long(self) -> None: ...
    def test_quiet_overrules_verbose(self) -> None: ...
    def test_output_folder_is_none_by_default(self) -> None: ...
    def test_output_folder_uses_filename_plus_timestamp_by_default(self) -> None: ...
    def test_output_folder_is_settable(self) -> None: ...
    def test_default_plot_is_false(self) -> None: ...
    def test_plot_is_settable(self) -> None: ...
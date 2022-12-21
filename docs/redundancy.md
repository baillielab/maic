# MAIC - redundant and unused code paths

This is a summary of unused and redundant code in the MAIC repository as of 08/12/2022.

Filenames and line numbers are as per commit `d50b558` on branch `master`

## Unused files:

The following files do not import any references from MAIC, and are not referenced anywhere else in the repository:

- `baseline.py`
- `evaluation-read.py`
- `evaluation-run.py`
- `dummy-imput-file.txt`

## Unused members:

The following constants and methods are either not referenced at all in the repository, or are only referenced from within the test files.


### `constants.py`
All declared constants *except* `T_METHOD_NONE`

### `cross_validation.py`

- `replace_list()` line 48
- **`code_string()` line 123 -- keep per BW, 14/12/2022**
- **`summary_data()` line 137 -- Keep per BW, 14/12/2022**
- `get_or_create_entity()` line 145

### `entity.py`

- `as_dict_for_json()` line 29
- **`score_from_list()` line 124** used in `maic/__init__.py` when constructing results

### `entitylist.py`

- `tell_entities_to_forget()` line 64
- `tell_entities_to_remember()` line 68
- `get_corrected_list_weight()` line 144
- `blank_copy()` line 204 and line 388
- `set_baseline()` line 211
- ALL subclasses of `EntityList` *except* `ExponentialEntityList`
    - `KnnEntityList` lines 223 - 254
    - `PolynomialEntityList` lines 255 - 287
    - `SvrEntityList` lines 288 - 320

* `get_entities()` (lines 72 **and** 208)
It is fortunate that this method is unused, as it has two definitions in the class with different return values.
**note: it turned out get_entities() was called, once, in a plotter implementation, but was only used to calculate the length of the entitylist. As EntityList defines a __len__ method, I have replaced the call (at `cv_plotter.py`, line 18) with a call to len(entity_list)**

### `options.py`

- `parsed_options.random_source_len` line 53

## Redundant Code

The following code is referenced elsewhere in MAIC (outside of testing) but has no impact on processing.

### Method chain from `calculate_final_corrected_scores()`

The following chain of methods is called as part of running the cross validation, theoretically looping through a list of passed correction methods to get final scores. However, there is no mechanism for passing correction methods into the code, therefore the entire chain has no effect. This chain is the only place that any of these methods are called outside of testing.

- `calculate_final_corrected_scores()` (`entity.py`, line 49)
- `get_final_weights_for_entity()` (`entitylist.py`, line 156)
- `adjusted_weight()` (`entitylist.py`, line 393)
- `sum_max_weights_per_category()` (`entity.py`, line 87)

### `code_string()` (`entitylist.py`, line 197)

Only called in the unused method `code_string()` (`cross_validation.py`, line 123)
**per BW 14/12/2022, worth keeping `code_string()` to assist consumers with debugging/tracking iterations**

### `_correct_fitted_weights() `(`entitylist.py`, line 215)

The body of this method has been commented out, so calling it literally does nothing.


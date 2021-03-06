T_METHOD_NONE = 'no_transform'
T_METHOD_MEAN = 'subtract-mean'
T_METHOD_STEM_SCALE = 'scaled_mean'
T_METHOD_STEM_ADJUST = 'adjusted_mean'
S_METHOD_NONE = 'no_scale'
S_METHOD_Z_TRANSFORM = 'z-transform'
S_METHOD_STEM_POW = 'pow'
TRANSFORM_STANDARD_OPTIONS = [T_METHOD_NONE, T_METHOD_MEAN]
TRANSFORM_EXTENDED_OPTIONS = [T_METHOD_STEM_SCALE, T_METHOD_STEM_ADJUST]
SCALE_STANDARD_OPTIONS = [S_METHOD_NONE, S_METHOD_Z_TRANSFORM]
SCALE_EXTENDED_OPTIONS = [S_METHOD_STEM_POW]
DEFAULT = '__default__'
SETTINGS_STRIP_COPY_TO_META = [
        # TODO: Update this for all relevant current attributes
        # TODO: Also include keyframes etc.!
        #   Is there a convenient way to copy all animation, transform, modifiers etc. between strips (or even better, link them)?
        'blend_type',
        'blend_alpha',
        'use_flip_x',
        'use_flip_y',
        # 'use_translation',
        # 'use_crop',
        'strobe',
        # 'playback_direction',
        'color_saturation',
        'color_multiply',
        'use_float',
        ['crop', 'min_x'],
        ['crop', 'max_x'],
        ['crop', 'min_y'],
        ['crop', 'max_y'],
        ['transform', 'offset_x'],
        ['transform', 'offset_y'],
    ]

SETTINGS_RESET_SOURCE_STRIP = {
        # TODO: Some properties must be set to custom values (e.g. blend_alpha, which will be reset to 0 otherwise)
        'blend_type': 'ALPHA_OVER',
        'blend_alpha': 1.,
        'use_flip_x': DEFAULT,
        'use_flip_y': DEFAULT,
        # 'use_translation',
        # 'use_crop',
        'strobe': DEFAULT,
        # 'playback_direction',
        'color_saturation': DEFAULT,
        'color_multiply': DEFAULT,
        'use_float': DEFAULT,
        ('crop', 'min_x'): DEFAULT,
    ('crop', 'max_x'): DEFAULT,
    ('crop', 'min_y'): DEFAULT,
    ('crop', 'max_y'): DEFAULT,
    ('transform', 'offset_x'): DEFAULT,
    ('transform', 'offset_y'): DEFAULT,
}
SETTINGS_STRIP_COPY_TO_COMP_STRIP = [

]
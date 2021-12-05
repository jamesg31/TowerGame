import pygame as pg
import numpy as np


def draw_line_dashed(
    surface, color, start_pos, end_pos, width=1, dash_length=10, exclude_corners=True
):

    # convert tuples to numpy arrays
    start_pos = np.array(start_pos)
    end_pos = np.array(end_pos)

    # get euclidian distance between start_pos and end_pos
    length = np.linalg.norm(end_pos - start_pos)

    # get amount of pieces that line will be split up in (half of it are amount of dashes)
    dash_amount = int(length / dash_length)

    # x-y-value-pairs of where dashes start (and on next, will end)
    dash_knots = np.array(
        [np.linspace(start_pos[i], end_pos[i], dash_amount) for i in range(2)]
    ).transpose()

    return [
        pg.draw.line(
            surface, color, tuple(dash_knots[n]), tuple(dash_knots[n + 1]), width
        )
        for n in range(int(exclude_corners), dash_amount - int(exclude_corners), 2)
    ]

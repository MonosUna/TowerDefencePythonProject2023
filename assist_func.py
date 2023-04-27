import constants


def get_x(selected_cell: tuple):
    x = selected_cell[1] * constants.CELL_SIZE + (constants.CELL_SIZE / 2)
    return x


def get_y(selected_cell: tuple):
    y = selected_cell[0] * constants.CELL_SIZE + (constants.CELL_SIZE / 2)
    return y

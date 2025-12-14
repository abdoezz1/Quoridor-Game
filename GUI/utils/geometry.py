def pixel_to_cell(x, y, widget_width, widget_height):
    cell_size = min(widget_width, widget_height) / 9
    return int(y // cell_size), int(x // cell_size)

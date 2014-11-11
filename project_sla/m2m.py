"""
Wrapper for OpenERP's cryptic write conventions for x2many fields.

Example usage:

    import m2m
    browse_rec.write({'many_ids: m2m.clear())
    browse_rec.write({'many_ids: m2m.link(99))
    browse_rec.write({'many_ids: m2m.add({'name': 'Monty'}))
    browse_rec.write({'many_ids: m2m.replace([98, 99]))

Since returned values are lists, the can be joined using the plus operator:

    browse_rec.write({'many_ids: m2m.clear() + m2m.link(99))

(Source: https://github.com/dreispt/openerp-write2many)
"""


def create(values):
    """ Create a referenced record """
    assert isinstance(values, dict)
    return [(0, 0, values)]


def add(values):
    """ Intuitive alias for create() """
    return create(values)


def write(id, values):
    """ Write on referenced record """
    assert isinstance(id, int)
    assert isinstance(values, dict)
    return [(1, id, values)]


def remove(id):
    """ Unlink and delete referenced record """
    assert isinstance(id, int)
    return [(2, id)]


def unlink(id):
    """ Unlink but do not delete the referenced record """
    assert isinstance(id, int)
    return [(3, id)]


def link(id):
    """ Link but do not delete the referenced record """
    assert isinstance(id, int)
    return [(4, id)]


def clear():
    """ Unlink all referenced records (doesn't delete them) """
    return [(5, 0)]


def replace(ids):
    """ Unlink all current records and replace them with a new list """
    assert isinstance(ids, list)
    return [(6, 0, ids)]


if __name__ == "__main__":
    # Tests:
    assert create({'name': 'Monty'}) == [(0, 0, {'name': 'Monty'})]
    assert write(99, {'name': 'Monty'}) == [(1, 99, {'name': 'Monty'})]
    assert remove(99) == [(2, 99)]
    assert unlink(99) == [(3, 99)]
    assert clear() == [(5, 0)]
    assert replace([97, 98, 99]) == [(6, 0, [97, 98, 99])]

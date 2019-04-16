def listify(items):
    """Puts each list element in its own list.

    Example:
        Input: [a, b, c]
        Output: [[a], [b], [c]]

    This is needed for tabulate to print rows [a], [b], and [c].

    Args:
        * items: A list to listify.

    Returns:
        A list that contains elements that are listified.
    """
    output = []
    for item in items:
        item_list = []
        item_list.append(item)
        output.append(item_list)
    return output

def print_error(message):
    """Prints the given message using click.secho with fg='red'.

    Args:
        * message: A string to be printed.

    Returns:
        None.
    """
    click.secho(message, fg='red')

def print_highlight(message):
    """Prints the given message using click.secho with fg='blue'.

    Args:
        * message: A string to be printed.

    Returns:
        None.
    """
    click.secho(message, fg='blue')

def print_items(items, headers):
    """Prints the items and headers with tabulate.

    Args:
        * items: A collection of items to print as rows with tabulate.
            Can be a list or dictionary.
        * headers: A collection of column headers to print with tabulate.
            If items is a list, headers should be a list.
            If items is a dictionary, set headers='keys'.

    Returns:
        None.
    """
    table = []
    for item in items:
        table.append(item)
    self._print_table(table, headers=headers)

def print_table(table, headers):
    """Prints the input table and headers with tabulate.

    Args:
        * table: A collection of items to print as rows with tabulate.
            Can be a list or dictionary.
        * headers: A collection of column headers to print with tabulate.
            If items is a list, headers should be a list.
            If items is a dictionary, set headers='keys'.

    Returns:
        None.
    """
    click.echo(tabulate(table, headers, tablefmt='grid'))



def return_elem_or_list(args):
    """Utility function to get a single element if len(args) == 1.

    Args:
        * args: A list of args.

    Returns:
        If args contains only one item, returns a single element.
        Else, returns args.
    """
    return args[0] if len(args) == 1 else args

class ParserFindTagException(Exception):
    """Вызывается, если не найден тег."""
    pass


class EmptyResponseEception(Exception):
    """Вызывается, если страница не загружена."""
    pass

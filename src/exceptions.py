class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass

class LatestVersionException(Exception):
    """Вызывается, когда парсер не может найти документацию."""
    pass
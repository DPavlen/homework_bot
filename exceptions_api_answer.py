class StatusOtherThan200Error(Exception):
    """Ответ от сервера не равный 200."""
    pass


class ApiRequestError(Exception):
    """Ошибка при запросе к API сервиса Практикум.Домашка."""
    pass


class UnexpectedError(Exception):
    """Произошла нестандартная ошибка."""
    pass


class JSONDecodeError(Exception):
    """Ошибка с преобразованием файла JSON."""
    pass


class EmptyResponseFromAPI(Exception):
    """Пустой ответ от API."""
    pass

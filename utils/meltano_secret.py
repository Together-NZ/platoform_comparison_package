MELTANO_MARKER = "meltano_"


def meltano_suffix_from_secret_name(secret_name: str) -> str:
    """Return the part after ``meltano_`` (e.g. Airflow variable key tail).

    ``airflow-variables-meltano_squirrel_main`` → ``squirrel_main``.

    If ``meltano_`` is missing, or nothing follows it, returns ``secret_name`` unchanged.
    """
    if MELTANO_MARKER not in secret_name:
        return secret_name
    _, _, suffix = secret_name.partition(MELTANO_MARKER)
    return suffix if suffix else secret_name

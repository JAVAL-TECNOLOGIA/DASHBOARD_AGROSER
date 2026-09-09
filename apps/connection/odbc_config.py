import platform


WINDOWS_SQLSERVER_DRIVER = "ODBC Driver 17 for SQL Server"
MACOS_SQLSERVER_DRIVER = "/opt/homebrew/lib/libtdsodbc.so"
DEFAULT_SQLSERVER_PORT = "1433"
MACOS_EXTRA_PARAMS = "TDS_Version=7.4;ClientCharset=UTF-8"


def is_windows():
    return platform.system() == "Windows"


def get_sqlserver_driver():
    if is_windows():
        return WINDOWS_SQLSERVER_DRIVER
    return MACOS_SQLSERVER_DRIVER


def get_django_db_options():
    if is_windows():
        return {
            "driver": get_sqlserver_driver(),
            "connect_timeout": 30,
        }

    return {
        "driver": get_sqlserver_driver(),
        "host_is_server": True,
        "connection_timeout": 30,
        "extra_params": MACOS_EXTRA_PARAMS,
    }


def build_pyodbc_connection_string(host, database, user, password, mars=False, port=DEFAULT_SQLSERVER_PORT):
    server = f"tcp:{host},{port}" if is_windows() else host
    parts = [
        f"DRIVER={get_sqlserver_driver()}",
        f"SERVER={server}",
        f"DATABASE={database}",
        f"UID={user}",
        f"PWD={password}",
    ]

    if not is_windows():
        parts.extend([
            f"PORT={port}",
            "TDS_Version=7.4",
            "ClientCharset=UTF-8",
        ])

    if mars:
        parts.append("MARS_Connection=yes")

    return ";".join(parts)

from typing import Callable, TypeVar

import streamlit.report_thread as ReportThread
# from streamlit import ReportThread
import streamlit.server as Server
# from streamlit.server import Server

T = TypeVar('T')


# noinspection PyProtectedMember
def get_state(setup_func: Callable[..., T], **kwargs) -> T:
    ctx = ReportThread.get_report_ctx()

    session = None
    session_infos = Server.get_current()._session_infos.values()

    for session_info in session_infos:
        if session_info.session._main_dg == ctx.main_dg:
            session = session_info.session

    if session is None:
        raise RuntimeError(
            "Oh noes. Couldn't get your Streamlit Session object"
            'Are you doing something fancy with threads?')

import subprocess
import threading
import uuid
import marimo as mo
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler


################################################################################
# Keeping global state
################################################################################

_data = {"get": None, "set": None}
_audio = {"get": None, "set": None}
_current_child = {"name": None}
_current_text = {"text": ""}
_current_session = []
_listened_to_words = []


################################################################################
# Static file server
################################################################################


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        return "tmp/" + path

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


def start_static_file_server_async():
    try:
        CORSRequestHandler.directory = "./tmp"
        httpd = HTTPServer(("0.0.0.0", 9999), CORSRequestHandler)
        httpd.serve_forever()
    except:
        pass


def start_static_file_server():
    thread = threading.Thread(target=start_static_file_server_async, args=[])
    thread.start()


################################################################################
# Generic utilities
################################################################################


def styles():
    return mo.Html(
        """
    <style>
    @font-face {
        font-family: "Cursive standard";
        src: url("https://quiet-rain-9918.fly.dev/public/cursive.woff") format("woff"), url("https://quiet-rain-9918.fly.dev/public/cursive.ttf") format("truetype");
        font-weight: normal;
        font-style: normal;
    }
    .cursive {
        font-family: "Cursive standard", sans-serif;
        line-height: normal;
    }
    </style>
    <div class="cursive">&nbsp;</div>
    """
    )


def cursive(text, color):
    html = f"""
    <div style="font-family: 'Cursive standard'; font-size: 30pt; line-height: normal; color:{color};">
    {text}
    </div>
    """
    return mo.Html(html)


def get_time():
    t = datetime.now()
    m = t.minute - (t.minute % 5)
    t = t.replace(minute=m, second=0, microsecond=0)
    return t.strftime("%Y-%m-%dT%H:%M")


################################################################################
# Click handlers
################################################################################


def gen_say_file(word):
    _rnd = uuid.uuid4()
    _rnd = f"marimo-audio-{_rnd}.wav"
    _fmt = "--data-format=LEF32@22050"
    params = ["say", "-v", "Thomas", "-r", "50", "-o", f"tmp/{_rnd}", _fmt, word]
    subprocess.run(params, capture_output=True, text=True, check=True)
    _audio["set"](_rnd)
    return word


def next(value):
    try:
        word, child = value
        if _current_text["text"] and len(_current_text["text"]) > 0:
            if not word in _listened_to_words:
                _listened_to_words.append(word)
                events = _data["get"]()
                event = {
                    "time": get_time(),
                    "child": child,
                    "type": "word",
                    "list": word["l"],
                    "word": word["w"],
                    "text": _current_text["text"],
                }
                events.append(event)
                _current_session.append(event)
                _data["set"](events)
        else:
            gen_say_file(word["w"])
    except Exception as e:
        print(e)
    return value


def record_input(value):
    _current_text["text"] = value
    return value


################################################################################
# UI Definition
################################################################################


def save_getset_data(getd, setd):
    _data["get"] = getd
    _data["set"] = setd


def save_getset_audio(getd, setd):
    _audio["get"] = getd
    _audio["set"] = setd


def next_question(courses, child, trigger):
    words = courses[child]["words"]
    verbs = courses[child]["verbs"]

    if _current_child["name"] != child:
        _current_session.clear()
        _listened_to_words.clear()
        _current_child["name"] = child

    if len(words) == 0:
        return (None, "Nothing to do")

    for word in words:
        # We've already gone through this word, skip
        if word in _listened_to_words:
            continue

        # Say it out lout
        text = word["w"]
        gen_say_file(text)

        # Generate UI elements
        input = mo.ui.text(
            placeholder="Type the word you hear / Ecris le mot que tu entends",
            on_change=record_input,
            full_width=True,
        )
        params = (word, child)
        listen = mo.ui.button(label="Listen again", value=text, on_click=gen_say_file)
        submit = mo.ui.button(label="Next word", value=params, on_click=next)
        iarray = mo.ui.array([input, listen, submit])
        vstack = mo.vstack(iarray.elements)
        return (iarray, vstack)

    # We are done. Generate table of results
    results = []
    for entry in _current_session:
        if entry["text"] == entry["word"]:
            results.append(
                {
                    "Typed": cursive(entry["text"], "green"),
                    "Correct": cursive(entry["word"], "black"),
                }
            )
        else:
            results.append(
                {
                    "Typed": cursive(entry["text"], "red"),
                    "Correct": cursive(entry["word"], "black"),
                }
            )
    table = mo.ui.table(data=results)
    return (None, table)

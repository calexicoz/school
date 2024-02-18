import marimo

__generated_with = "0.2.5"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def __():
    import marimo as mo
    import csv
    import json
    import subprocess
    import importlib
    from datetime import datetime

    # Mine
    import helpers

    helpers.styles()
    return csv, datetime, helpers, importlib, json, mo, subprocess


@app.cell(hide_code=True)
def __(csv, helpers, json, mo):
    events = []
    courses = {}
    try:
        with open("data.csv", mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                events.append(row)
        with open("courses.json", "r") as _file:
            courses = json.load(_file)
    except:
        pass

    getd, setd = mo.state(events)
    geta, seta = mo.state("")
    helpers.save_getset_data(getd, setd)
    helpers.save_getset_audio(geta, seta)
    helpers.start_static_file_server()
    return courses, events, file, geta, getd, reader, row, seta, setd


@app.cell(hide_code=True)
def __(csv, getd):
    with open("data.csv", "w") as _file:
        if len(getd()) > 0:
            fieldnames = getd()[0].keys()
            writer = csv.DictWriter(_file, fieldnames=fieldnames)
            writer.writeheader()
            for entry in getd():
                writer.writerow(entry)
    return entry, fieldnames, writer


@app.cell(hide_code=True)
def __(mo):
    child_selector = mo.ui.dropdown(options=["Huey", "Jesse"])
    child_selector
    return child_selector,


@app.cell(hide_code=True)
def __(child_selector, courses, helpers, mo, trigger):
    mo.stop(child_selector.value is None, "Please select a child")
    iarray, vstack = helpers.next_question(courses, child_selector.value, trigger)
    vstack
    return iarray, vstack


@app.cell(hide_code=True)
def __(geta, mo):
    mo.Html(f"""<audio src="http://192.168.8.100:9999/{geta()}" autoplay></audio>""")
    return


@app.cell(hide_code=True)
def __(datetime, getd):
    trigger = datetime.now()
    getd()
    None
    return trigger,


if __name__ == "__main__":
    app.run()

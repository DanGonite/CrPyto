import io
import operator
from string import ascii_lowercase as ALPH

import matplotlib.pyplot as plt
from flask import Blueprint, Response, render_template, request, url_for
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from Formatting import PuncRem, SpaceAdd, SpaceRem
from Processing import DetectEnglish, FreqAnalysis

tools = Blueprint("tools", __name__, url_prefix="/tools")

methods = ["GET", "POST"]

@tools.route("/freqanalysis.html", methods=methods)
def freqAnalysis():
    args = {"title": "Frequency Analysis", "ciphText": "", "result": "", "score": 0, "vals": {}, "keylen": ""}
    if request.method == "POST":
        args["ciphText"] = request.form["ciphInput"]
    plotFreq(args["ciphText"])
    return render_template(f"tools/freqanalysis.html", **args)


@tools.route("/addspaces.html", methods=methods)
def addSpaces():
    args = {"title": "Add Spaces", "ciphText": "", "result": "", "score": 0, "vals": {}, "keylen": ""}
    if request.method == "POST":
        args["ciphText"] = ciph = request.form["ciphInput"]
        args["result"] = plain = SpaceAdd.add(ciph)
        args["score"] = DetectEnglish.detectWord(plain) * 100
    return render_template(f"tools/addspaces.html", **args)


@tools.route("/removespaces.html", methods=methods)
def removeSpaces():
    args = {"title": "Remove Spaces", "ciphText": "", "result": "", "score": 0, "vals": {}, "keylen": ""}
    if request.method == "POST":
        args["ciphText"] = ciph = request.form["ciphInput"]
        args["result"] = plain = SpaceRem.remove(ciph)
        args["score"] = DetectEnglish.detectWord(SpaceAdd.add(plain)) * 100
    return render_template(f"tools/removespaces.html", **args)


@tools.route("/removepunctuation.html", methods=methods)
def removePunctuation():
    args = {"title": "Remove Punctuation", "ciphText": "", "result": "", "score": 0, "vals": {}, "keylen": ""}
    if request.method == "POST":
        args["ciphText"] = ciph = request.form["ciphInput"]
        args["result"] = plain = PuncRem.remove(ciph)
        args["score"] = DetectEnglish.detectWord(SpaceAdd.add(plain)) * 100
    return render_template(f"tools/removepunctuation.html", **args)


@tools.route("/reversetext.html", methods=methods)
def reverseText():
    args = {"title": "Reverse Text", "ciphText": "", "result": "", "score": 0, "vals": {}, "keylen": ""}
    if request.method == "POST":
        args["ciphText"] = ciph = request.form["ciphInput"]
        args["result"] = plain = ciph[::-1]
        args["score"] = DetectEnglish.detectWord(SpaceAdd.add(plain)) * 100
    return render_template(f"tools/reversetext.html", **args)


def plotFreq(ciph):
    fig, ax = plt.subplots(figsize=(10, 5))
    barwidth = 0.3

    lettcounts = [FreqAnalysis.englishProbabilities.get(x, 0) for x in ALPH]
    ciphprobs = FreqAnalysis.getFrequencies(ciph)
    ax.bar([x for x in map(operator.sub, range(len(lettcounts)), [barwidth / 2] * len(lettcounts))], lettcounts, width=barwidth, label="English", color="r")
    try:
        ciphcounts = [ciphprobs.get(x, 0) / len(ciph) for x in sorted(ALPH)]
        ax.bar([x for x in map(operator.add, range(len(ciphprobs)), [barwidth / 2] * len(ciphcounts))], ciphcounts, width=barwidth, label="Cipher Text", color="b")
    except ZeroDivisionError:
        pass
    ax.get_yaxis().set_visible(False)
    ax.set_xticks(range(len(ALPH)))
    ax.set_xticklabels(map(str.upper, sorted(ALPH)))
    ax.legend()

    fig.savefig(url_for("static", filename="img/freqanalysis.png"))

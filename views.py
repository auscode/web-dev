from operator import eq

from numpy import equal
from . import util
import secrets
from django import forms
from markdown2 import Markdown as md
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render


def index(request):
    return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})


def entry(request, title):
    Page = util.get_entry(title)
    if Page is None:
        return render(request, "encyclopedia/notFound.html", {"title": title})
    else:
        return render(
            request,
            "encyclopedia/entry.html",
            {"titlePage": md().convert(Page), "title": title},
        )


# def search(request):
#     query = request.GET.get("q", "")
#     if util.get_entry(query) is not None:
#         return HttpResponseRedirect(reverse("entry", kwargs={"entry": query}))
#     else:
#         querySet = []
#         for entry in util.list_entries():
#             if query.upper() in entry.upper():
#                 querySet.append(entry)

#         return render(
#             request,
#             "encyclopedia/index.html",
#             {"entries": querySet, "search": True, "query": query},
#         )
def search(request):
    keyword = util.list_entries()
    keyList = list()

    key = request.GET.get("q")
    # match=util.get_entry(key)

    if key.upper() in keyword:
        return HttpResponseRedirect(f"wiki/{key}")

    for entry in keyword:
        if key.upper() in entry.upper():
            keyList.append(entry)
    if keyList:
        return render(request, "encyclopedia/index.html", {
            "search_result": keyList,
            "search": key
        })
    else:
        return render(request, "encyclopedia/notfound.html")


class NewEntryForm(forms.Form):
    title = forms.CharField(
        label="Entry title",
        widget=forms.TextInput(
            attrs={"class": "form-control col-md-8col-lg-8"}),
    )
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control col-md-8col-lg-8", "rows": 8}
        )
    )
    edit = forms.BooleanField(
        initial=False, widget=forms.HiddenInput(), required=False)


def newentry(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if util.get_entry(title) is None or form.cleaned_data["edit"] is True:
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("entry", kwargs={"entry": title}))
            else:
                return render(
                    request,
                    "encyclopedia/newpage.html",
                    {"form": form, "existing": True, "entry": title}
                )
        else:
            return render(
                request, "encyclopedia/newpage.html", {
                    "form": form, "existing": False}
            )
    else:
        return render(
            request,
            "encyclopedia/newpage.html",
            {"form": NewEntryForm(), "existing": False}
        )


def edit(request, entry):
    entrypage = util.get_entry(entry)
    if entrypage is None:
        return render(request, "encyclopedia/notFound.html", {
            "title": entry
        })
    else:
        form = NewEntryForm()
        form.fields["title"].initial = entry
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = entrypage
        form.fields["edit"].initial = True

        return render(request, "encyclopedia/newpage.html", {
            "form": form,
            "edit": form.fields["edit"].initial,
            "title": form.fields["title"].initial
        })


def random(request):
    randomPage = secrets.choice(util.list_entries())
    randomitem = util.get_entry(randomPage)
    return render(request, "encyclopedia/entry.html", {
        "title": randomPage,
        "titlePage": md().convert(randomitem)
    })

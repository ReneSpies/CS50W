from django.shortcuts import render
from markdown import Markdown
from . import util
from django import forms
from django.http import HttpResponseRedirect
import random


def index(request):
    # Return a list of all entries
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, name):
    markdown = Markdown()

    # Get the entry from the markdown file
    markdown_entry = util.get_entry(name)

    html_from_markdown = None

    # Convert the markdown to HTML
    if markdown_entry is not None:
        html_from_markdown = markdown.convert(markdown_entry)

    # Display the entry in HTML
    return render(request, f"encyclopedia/entry.html", {
        "title": name.capitalize(),
        "content": html_from_markdown,
    })


def search(request):
    # Extract the query from the request in lowercase
    query = request.GET.get('q', None).lower()

    # Get all entries
    entries = util.list_entries()

    # Lower all entries and save those in a new list
    lowercase_entries = [entry.lower() for entry in entries]

    # Display the entry if one is found by the query
    if query in lowercase_entries:
        return HttpResponseRedirect(f"../wiki/{query}")

    similar_entries = list()

    # Search for similar entries if query does not match one
    for entry in entries:

        if query in entry.lower() and query != entry.lower():
            similar_entries.append(entry)

    # Show an error page if there are no similar entries
    # else, list all similar entries
    if len(similar_entries) == 0:

        return render(request, "encyclopedia/entry.html", {
            "title": None,
            "content": None,
        })

    else:

        return render(request, "encyclopedia/index.html", {
            "entries": similar_entries,
        })


def create(request):
    if request.method == "POST":

        title_form = TitleForm(request.POST)
        content_form = ContentForm(request.POST)

        if title_form.is_valid() and content_form.is_valid():

            title_text = title_form.cleaned_data["title_form"]
            content_text = content_form.cleaned_data["content_form"]

            lowercase_existing_entries = [entry.lower() for entry in util.list_entries()]

            if title_text.lower() in lowercase_existing_entries:

                return render(request, "encyclopedia/entry.html", {
                    "title": "Already exists",
                    "content": None
                })

            else:

                util.save_entry(title_text, content_text)

                return HttpResponseRedirect(f"../wiki/{title_text}")

        else:

            return render(request, "encyclopedia/create.html", {
                "title_form": title_form,
                "content_form": content_form
            })

    return render(request, "encyclopedia/create.html", {
        "title_form": TitleForm,
        "content_form": ContentForm
    })


def edit(request, title):
    current_content = util.get_entry(title)

    if request.method == "POST":

        edit_form = EditForm(request.POST)

        if edit_form.is_valid():

            edited_content = edit_form.cleaned_data["edit_form"]

            util.save_entry(title, edited_content)

            return HttpResponseRedirect(f"../wiki/{title}")

    edit_form = EditForm
    edit_form.value = current_content

    return render(request, "encyclopedia/edit.html", {
        "entry_name": title,
        "edit_form": edit_form
    })


def random_page(request):
    all_entries = util.list_entries()
    total_page_count = len(all_entries)

    chosen_index = random.randrange(total_page_count)

    chosen_entry = all_entries[chosen_index]

    print(f"chosen entry = {chosen_entry}")

    return HttpResponseRedirect(f"../wiki/{chosen_entry}")


class TitleForm(forms.Form):
    title_form = forms.CharField(label="Title")


class ContentForm(forms.Form):
    content_form = forms.CharField(widget=forms.Textarea(), label="")


class EditForm(forms.Form):
    value = ""
    edit_form = forms.CharField(widget=forms.Textarea(), label="")

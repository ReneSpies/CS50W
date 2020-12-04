from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, AuctionListing


def index(request):
    return HttpResponseRedirect(reverse("auctions:listings_by_category", kwargs={"category": "all"}))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


@login_required(login_url="auctions:login")
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url="auctions:login")
def create_listing_view(request):
    if request.method == "POST":
        title_form = TitleForm(request.POST)
        description_form = DescriptionForm(request.POST)
        bidding_form = BiddingForm(request.POST)
        print(f"post = {request.POST}")
        if title_form.is_valid() and description_form.is_valid() and bidding_form.is_valid():
            title = request.POST["title_form"]
            description = request.POST["description_area"]
            starting_bid = request.POST["bidding_form"]
            image_url = request.POST["image_url_form"]
            category = request.POST["category_form"]
            user = request.user

            try:
                category = Category.objects.get(title=category)
                new_listing = AuctionListing(title=title, description=description, highest_bid=starting_bid,
                                             image_url=image_url, category=category, owner=user)
                new_listing.save()
            except Category.DoesNotExist:
                new_listing = AuctionListing(title=title, description=description, highest_bid=starting_bid,
                                             image_url=image_url, category=None, owner=user)
                new_listing.save()

    return render(request, "auctions/create_listing.html", {
        "title_form": TitleForm,
        "description_area": DescriptionForm,
        "bidding_form": BiddingForm,
        "image_url_form": ImageURLForm,
        "categories": Category.objects.all()
    })


@login_required(login_url="auctions:login")
def watchlist_view(request):
    return render(request, "auctions/watchlist.html")


@login_required(login_url="auctions:login")
def categories_view(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def listings_by_category_view(request, category):
    if category == "all":
        # Show all listings
        listings = AuctionListing.objects.all()
    else:
        try:
            category = Category.objects.get(title=category)
            listings = AuctionListing.objects.filter(category=category)
        except Category.DoesNotExist:
            return render(request, "auctions/listings_by_category.html", {
                "error_message": "No category found by that name"
            })
        except AuctionListing.DoesNotExist:
            return render(request, "auctions/listings_by_category.html", {
                "error_message": "No listings for this category"
            })
    return render(request, "auctions/listings_by_category.html", {
        "category": category,
        "listings": listings
    })


@login_required(login_url="auctions:login")
def listing_view(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bidding_form": BiddingForm,
        "comment_form": CommentForm
    })


class DescriptionForm(forms.Form):
    description_area = forms.CharField(widget=forms.Textarea(attrs={"placeholder": "Description"}), label="")


class TitleForm(forms.Form):
    title_form = forms.CharField(label="", max_length=64, widget=forms.TextInput(attrs={"placeholder": "Title"}))


class BiddingForm(forms.Form):
    bidding_form = forms.IntegerField(min_value=1, help_text="€", label="Bid")


class ImageURLForm(forms.Form):
    image_url_form = forms.URLField(label="Image URL", widget=forms.URLInput(attrs={"placeholder": "(optional)"}),
                                    required=False)


class CommentForm(forms.Form):
    comment_area = forms.CharField(widget=forms.Textarea, label="")

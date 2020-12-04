from django.urls import path

from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register_view, name="register"),
    path("create-listing", views.create_listing_view, name="create_listing"),
    path("watchlist", views.watchlist_view, name="watchlist"),
    path("categories", views.categories_view, name="categories"),
    path("category/<str:category>", views.listings_by_category_view, name="listings_by_category"),
    path("listing/<int:listing_id>", views.listing_view, name="listing")
]

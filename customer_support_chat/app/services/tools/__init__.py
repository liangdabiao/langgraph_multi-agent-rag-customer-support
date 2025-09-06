# customer_support_chat/app/services/tools/__init__.py

from .lookup import lookup_policy, search_faq
from .flights import (
    fetch_user_flight_information,
    search_flights,
    update_ticket_to_new_flight,
    cancel_ticket,
)
from .cars import (
    search_car_rentals,
    book_car_rental,
    update_car_rental,
    cancel_car_rental,
)
from .hotels import (
    search_hotels,
    book_hotel,
    update_hotel,
    cancel_hotel,
)
from .excursions import (
    search_trip_recommendations,
    book_excursion,
    update_excursion,
    cancel_excursion,
)
# New tools for extended functionalities
from .woocommerce import search_products, search_orders
from .forms import submit_form
from .blog import search_blog_posts

__all__ = [
    "lookup_policy",
    "search_faq",
    "fetch_user_flight_information",
    "search_flights",
    "update_ticket_to_new_flight",
    "cancel_ticket",
    "search_car_rentals",
    "book_car_rental",
    "update_car_rental",
    "cancel_car_rental",
    "search_hotels",
    "book_hotel",
    "update_hotel",
    "cancel_hotel",
    "search_trip_recommendations",
    "book_excursion",
    "update_excursion",
    "cancel_excursion",
    # New tools
    "search_products",
    "search_orders",
    "submit_form",
    "search_blog_posts",
]

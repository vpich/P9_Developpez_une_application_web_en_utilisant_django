from django import template
import locale
locale.setlocale(locale.LC_TIME, '')


register = template.Library()


@register.filter
def model_type(value):
    return type(value).__name__


@register.simple_tag(takes_context=True)
def get_poster_display(context, user):
    if user == context["user"]:
        return "Vous"
    return f"{user.username}"


@register.simple_tag(takes_context=True)
def get_verb_display(context, user):
    if user == context["user"]:
        return "avez"
    return "a"


@register.simple_tag(takes_context=True)
def get_posted_at_display(context, date_created):
    date = date_created.strftime('%H:%M, %d %B %Y')
    return f"{date}"


@register.simple_tag(takes_context=True)
def get_review_stars_display(context, rating):
    black_star = "&starf;"
    white_star = "&star;"

    black_stars_number = rating * black_star
    white_star_number = (5 - rating) * white_star

    return f"{black_stars_number}{white_star_number}"

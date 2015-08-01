from django import template

register = template.Library()

@register.filter
def truncate_query_parameters(url):
    index = url.index('?')
    return url[:index]


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginate(request, queryset, per_page=20):
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj

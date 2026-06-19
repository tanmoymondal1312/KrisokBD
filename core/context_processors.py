def nav_active(request):
    path = request.path

    if path == '/':
        section = 'home'
    elif path.startswith('/prices/'):
        section = 'market'
    elif '/marketplace/profile' in path or path == '/marketplace/profiles/':
        section = 'profiles'
    elif path.startswith('/marketplace/'):
        section = 'buysell'
    elif path.startswith('/content/videos/'):
        section = 'others'
    elif path.startswith('/content/govt-prices/'):
        section = 'others'
    elif path.startswith('/content/analysis/'):
        section = 'others'
    else:
        section = ''

    sub = ''
    if '/prices/daily/' in path:
        sub = 'daily'
    elif '/prices/division/' in path:
        sub = 'division'
    elif '/prices/comparison/' in path:
        sub = 'comparison'
    elif '/prices/regional/' in path:
        sub = 'regional'
    elif '/prices/market/' in path:
        sub = 'market_detail'
    elif '/prices/product/' in path:
        sub = 'product_detail'
    elif '/content/videos/' in path:
        sub = 'videos'
    elif '/content/govt-prices/' in path:
        sub = 'govt'
    elif '/content/analysis/' in path:
        sub = 'analysis'

    return {'nav_section': section, 'nav_sub': sub}

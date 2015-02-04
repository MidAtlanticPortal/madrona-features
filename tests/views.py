from django.http import HttpResponse

def habitat_spreadsheet(request, instance):
    return HttpResponse('Report Contents')

def kml(request, instances):
    return HttpResponse('<kml />')

def valid_single_select_view(request, instance):
    return HttpResponse(instance.name)

def invalid_single_select_view(request, pk):
    pass

def invalid_multiple_select_view(request, fail):
    pass

def valid_multiple_select_view(request, instances):
    return HttpResponse(', '.join([i.name for i in instances]))
def multi_select_view(request, instances):
    return HttpResponse(', '.join([i.name for i in instances]))
def delete_w_contents(request, instances):
    return HttpResponse('Deleted')

def viewshed_map(request, instance):
    return HttpResponse('image')

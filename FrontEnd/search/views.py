import json
import traceback
import sys
import csv
import os

from functools import reduce
from operator import and_

from django.shortcuts import render
from django import forms

from search_items import search

NOPREF_STR = 'No preference'
RES_DIR = os.path.join(os.path.dirname(__file__), '..', 'res')
COLUMN_NAMES = dict(
    stores='Stores',
    product_name="Product Name",
    store_address="Store Address",
    ingredients="ingredients"
)


def _valid_result(res):
    """Validate results returned by search."""
    (HEADER, RESULTS) = [0, 1]
    ok = (isinstance(res, (tuple, list)) and
          len(res) == 2 and
          isinstance(res[HEADER], (tuple, list)) and
          isinstance(res[RESULTS], (tuple, list)))
    if not ok:
        return False

    n = len(res[HEADER])

    def _valid_row(row):
        return isinstance(row, (tuple, list)) and len(row) == n
    return reduce(and_, (_valid_row(x) for x in res[RESULTS]), True)


STORS = [('', NOPREF_STR), ('Whole Foods', 'Whole Foods'),
         ('Jewel Osco', 'Jewel Osco'), ('Trader Joes', 'Trader Joes')]
LABELS = [('', NOPREF_STR), ('organic', 'Organic'), ('vegan', 'Vegan'),
          ('dairy free', 'Dairy Free'), ('kosher', 'Kosher')]


class SearchForm(forms.Form):
    product_name = forms.CharField(label='Search item names:',
                                   help_text='e.g. Yogurt',
                                   required=False)
    stores = forms.MultipleChoiceField(label='Stores', choices=STORS,
                                       widget=forms.CheckboxSelectMultiple,
                                       required=False)
    calories = forms.CharField(label='Calories <=', required=False)
    tot_fat = forms.CharField(label='Total Fat (g) <=', required=False)
    trans_fat = forms.CharField(label='Trans Fat (g) <=', required=False)
    sodium = forms.CharField(label='Sodium (mg) <=', required=False)
    tot_carhy = forms.CharField(
        label='Total Carbhydrate (g) <=', required=False)
    protein = forms.CharField(label='Protein (g) >=', required=False)
    sugars = forms.CharField(label='Sugars (g) <=', required=False)
    labels = forms.MultipleChoiceField(label='Dietary Restrictions', choices=LABELS,
                                       widget=forms.CheckboxSelectMultiple,
                                       required=False)
    contains = forms.CharField(label='Contains:',
                               help_text='e.g. Whole Milk',
                               required=False)
    not_contain = forms.CharField(label='Do Not Contain:',
                                  help_text='e.g. Wheat',
                                  required=False)
    zipcode = forms.CharField(label='Zipcode:',
                              help_text='To find stores nearby, please enter your zipcode',
                              required=False)
    show_args = forms.BooleanField(label='Show args_to_ui', required=False)


def home(request):
    context = {}
    res = None
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # check whether it's valid:
        if form.is_valid():

            # Convert form data to an args dictionary for search
            args = {}
            if form.cleaned_data['product_name']:
                args['product_name'] = form.cleaned_data['product_name']
            if form.cleaned_data['stores']:
                args['store_name'] = form.cleaned_data['stores']
            if form.cleaned_data['calories']:
                args['calories'] = form.cleaned_data['calories']
            if form.cleaned_data['trans_fat']:
                args['trans_fat'] = form.cleaned_data['trans_fat']
            if form.cleaned_data['tot_fat']:
                args['tot_fat'] = form.cleaned_data['tot_fat']
            if form.cleaned_data['sodium']:
                args['sodium'] = form.cleaned_data['sodium']
            if form.cleaned_data['tot_carhy']:
                args['tot_carhy'] = form.cleaned_data['tot_carhy']
            if form.cleaned_data['protein']:
                args['protein'] = form.cleaned_data['protein']
            if form.cleaned_data['sugars']:
                args['sugars'] = form.cleaned_data['sugars']
            if form.cleaned_data['labels']:
                args['labels'] = form.cleaned_data['labels']
            if form.cleaned_data['contains']:
                args['contains'] = form.cleaned_data['contains']
            if form.cleaned_data['not_contain']:
                args['not_contain'] = form.cleaned_data['not_contain']
            if form.cleaned_data['zipcode']:
                args['zipcode'] = str(form.cleaned_data['zipcode'])
            if form.cleaned_data['show_args']:
                context['args'] = 'args_to_ui = ' + json.dumps(args, indent=2)

            try:
                res = search(args)
            except Exception as e:
                print('Exception caught')
                bt = traceback.format_exception(*sys.exc_info()[:3])
                context['err'] = """
                An exception was thrown in search:
                <pre>{}
{}</pre>
                """.format(e, '\n'.join(bt))

                res = None
    else:
        form = SearchForm()

    # Handle different responses of res
    if res is None:
        context['result'] = None
    elif isinstance(res, str):
        context['result'] = None
        context['err'] = res
        result = None
    elif not _valid_result(res):
        context['result'] = None
        context['err'] = ('Return of search has the wrong data type. ')
    else:
        columns, result = res

        # Wrap in tuple if result is not already
        if result and isinstance(result[0], str):
            result = [(r,) for r in result]

        context['result'] = result
        context['num_results'] = len(result)
        context['columns'] = [COLUMN_NAMES.get(col, col) for col in columns]

    context['form'] = form
    return render(request, 'index.html', context)

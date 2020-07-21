from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers

from .models import Choice, Question, DiseaseRank
from .rank_phenotypes import rank_phenotypes_tfidf
import json

# Create your views here.
class IndexView(generic.ListView):
    model = DiseaseRank
    template_name = 'ranks/index.html'
    context_object_name = 'rankings'

    def get_rankings(self):
        """Return the rankings"""
        return DiseaseRank.objects;

class DetailView(generic.DetailView):
    model = Question
    template_name = 'ranks/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'ranks/results.html'

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'ranks/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('ranks:results', args=(question.id,)))

@csrf_exempt
# def rank(req):
#     hp = []
#     if req.method == 'GET':
#         hp = req.GET.get('phenotypes').split(',')
#     results = []
#     if len(hp) > 0:
#         rank = rank_phenotypes_tfidf(hp)
#         for i, r in enumerate(rank):
#             results.append({
#                 'score': r[0],
#                 'id': r[1]['id'],
#                 'disease': r[1]['name'],
#                 'phenotypes': list(r[2])
#                 })
#     return HttpResponse(json.dumps('ranks:index, indent=2), content_type='application/json', status=200)
def rank(req):
    hp = []
    if req.method == 'GET':
        hp = req.GET.get('phenotypes').split(',')
    results = []
    if len(hp) > 0:
        rank = rank_phenotypes_tfidf(hp)
        for i, r in enumerate(rank):
            dis = DiseaseRank(ontology_id = r[1]['id'], disease_name = r[1]['name'], score =r[0], phenotypes=list(r[2]))
            results.append(dis)
    return HttpResponseRedirect('ranks:index')

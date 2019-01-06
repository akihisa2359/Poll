from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
import io
import matplotlib.pyplot as plt
import numpy as np

from .models import Choice, Question, Age

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
   question = get_object_or_404(Question, pk=question_id)
   return render(request, 'polls/detail.html', {
       'question': question,
	   })

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    choices = question.choice_set.all()
    return render(request, 'polls/results.html', {
        'question': question,
        'choices': choices,
        })

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_age_id = ((int(request.POST['choice']) - 1) * 6) + int(request.POST['age'])
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
        selected_choice_age = selected_choice.age_set.get(pk=selected_age_id)
    except (KeyError, Choice.DoesNotExist, Age.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice_age.votes += 1
        selected_choice_age.save()
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    
# グラフ作成
def setPlt(pk):
	question = get_object_or_404(Question, pk=pk)
	choices = question.choice_set.all()
	
	N, K = len(Age.range_list), choices.count()
	data = []
	
	for choice in choices:
		for age in choice.age_set.all():
			data.append(age.votes)
	
	data = np.reshape(data, (N, K), order="F") #列ごとにchoiceの結果を格納する
	
	normalized = data / data.sum(axis=1, keepdims=True) #6行2列を維持したまま比率を取得
	cumulative = np.zeros(N)
	tick = np.arange(N)
	cmap = plt.get_cmap("tab10")

	for k in range(K):
		color = plt.cm.autumn(float(k) / K, 1)
		plt.barh(tick, normalized[:, k], left=cumulative, color=color, label=choices[k]) #k列のグラフをN行分leftに積み上げる
		cumulative += normalized[:, k]

	plt.xlim((0, 1))
	plt.xlabel("rate")
	plt.ylabel("age")
	plt.yticks(tick, Age.range_list)
	plt.legend()
	plt.plot()
 
 
# svgへの変換
def pltToSvg():
    buf = io.BytesIO()
    plt.savefig(buf, format='svg', bbox_inches='tight')
    s = buf.getvalue()
    buf.close()
    return s
 
 
def get_svg(request, pk):
    setPlt(pk)       # create the plot
    svg = pltToSvg() # convert plot to SVG
    plt.cla()        # clean up plt so it can be re-used
    response = HttpResponse(svg, content_type='image/svg+xml')
    return response

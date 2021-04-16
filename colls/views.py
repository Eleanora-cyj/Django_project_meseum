from colls.models import Coll, Comment, Fav
from colls.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.core.files.uploadedfile import InMemoryUploadedFile

from colls.forms import CreateForm
from colls.forms import CommentForm

from django.contrib.humanize.templatetags.humanize import naturaltime

from django.db.models import Q
from colls.utils import dump_queries

import nltk
import pandas as pd
from rank_bm25 import BM25Okapi
from stemming.porter2 import stem

# from nltk.stem.porter import PorterStemmer
# ps = PorterStemmer()
# from nltk.stem import WordNetLemmatizer
# wl = WordNetLemmatizer()
# from sklearn.feature_extraction.text import CountVectorizer
# from wordcloud import WordCloud, STOPWORDS
# stopwords = set(STOPWORDS)
# import string 
# import re

def merge_list(data):
    string=''
    for d in data:
        if type(d)==str:
            string+= "/n"+d
        else:
            for a in d:
                string+="/n"+a
    return string


def index(request):
    res_list = []
    query = ''
    # pre-process
    nltk.download('punkt')

    module_dir = os.path.dirname(__file__)  
    txt_file_path = os.path.join(module_dir, 'stoplist.txt')
    document = open(txt_file_path,'r',encoding='UTF-8')
    stoplist = document.read()
    document.close()
    stoplist = stoplist.split()
    stoplist = [word.lower() for word in stoplist]

    csv_file_path = os.path.join(module_dir, 'museum_data_new.csv')
    museum_df = pd.read_csv(csv_file_path, converters={'column_name': eval})

    temp_result = museum_df[museum_df['museum']=='British Museum'].description.apply(eval)
    for _ in temp_result:
        _ = str(merge_list(_))

    museum_df[museum_df['museum']=='British Museum'].description = temp_result
    museum_df['description'] = museum_df['description'].apply(lambda x:str(x))


    def data_process(description, date = False):
        tokens = nltk.word_tokenize(description)
        if date:
            filter_words = [word.lower() for word in tokens if word.lower() not in stoplist]
        else:
            filter_words = [stem(word.lower()) for word in tokens if word.lower() not in stoplist and word.isalpha()]
        return filter_words

    # def comment_cleaning(text, contraction = False, stop_word = True, stem = True, lemma = False):

    #     text = str(text).lower()
        
    #     # Contractions 
    #     if contraction:
    #         text = text.split()
    #         new_text = []
    #         for _ in text:
    #             if _ in contraction:
    #                 new_text.append(contraction[_])
    #             else:
    #                 new_text.append(_)
    #         text = " ".join(new_text)
        
    #     text = re.sub(r'https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
    #     text = re.sub(r'\<a href', ' ', text)
    #     text = re.sub(r'&amp;', '', text) 
    #     text = re.sub(r'[_"\-;%()|+&=*%.,!?:#$@\[\]/]', ' ', text)
    #     text = re.sub(r'<br />', ' ', text)
    #     text = re.sub(r'\'', ' ', text)
    #     text = str(text).lower()
    #     text = re.sub(r'\[.*?\]', '', text)
    #     # text = re.sub(r'https?://\S+|www\.\S+', '', text)
    #     text = re.sub(r'<.*?>+', '', text)
    #     text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
    #     text = re.sub(r'\n', '', text)
    #     text = re.sub(r'\w*\d\w*', '', text)

    #     # Remove stopwords or use stemming
    #     text = text.split()
    #     if stop_word:
    #         text = [w for w in text if not w in stopwords]
    #         if lemma:
    #             text = [wl.lemmatize(w) for w in text]
    #         if stem: 
    #             text = [ps.stem(w) for w in text]
    #     text = " ".join(text)
        
    #     return text

    # column_list = ['title','artist','culture','place','category','date','description']
    # corpus = []
    # for i in range(7):
    #     corpus.append(museum_df[column_list[i]].tolist())

    # tokenized_corpus = []
    # for j in range(7):
    #     tokenized_corpus.append([comment_cleaning(str(doc)).split(" ") for doc in corpus[j]])

    # def score_calculator(query, title_weight = 5, artist_weight = 4, culture_weight = 4, place_weight = 4, category_weight = 4, date_weight = 4, description_weight = 1):
    #     bm25 = []
    #     for k in range(7):
    #         bm25.append(BM25Okapi(tokenized_corpus[k]))
        
    #     score = []
    #     for l in range(7):
    #         score.append(bm25[i].get_scores(data_process(query)))

    #     score_total = score[0]*title_weight + score[1]*artist_weight + score[2]*culture_weight + score[3]*place_weight + score[4]*category_weight + score[5]*date_weight + score[6]*description_weight
        
    #     museum_score  = museum_df.copy()
    #     museum_score['score'] = score_total
    #     museum_score = museum_score.sort_values(by = 'score', ascending = False)
    #     return museum_score

    # query
    if request.method=="POST":
        query = request.POST.get('query')
        tokenized_query = data_process(query)
        RES_NUM = 5
        musemu_list = ['British Museum','Brooklyn Museum','The Metropolitan Museum of Art']
        for i, muse in enumerate(musemu_list):
            part_museum_df = museum_df[museum_df['museum']==muse]
            corpus = part_museum_df['description'].drop_duplicates("first").tolist()
            tokenized_corpus = [str(doc).split(" ") for doc in corpus]
            bm25 = BM25Okapi(tokenized_corpus)
            res = bm25.get_top_n(tokenized_query, corpus, n=RES_NUM)
            if i==0:
                res_df = part_museum_df[part_museum_df['description'].isin(res)]
            else:
                res_df = pd.concat([res_df, part_museum_df[part_museum_df['description'].isin(res)]])
        res_list = res_df.T.to_dict().values()
    return render(request, 'index.html',{'collection_list':res_list,'query':query})

class CollListView(OwnerListView):
    model = Coll
    template_name = "colls/coll_list.html"

    def get(self, request):
        strval =  request.GET.get("query", False)
        if strval :
            query = Q(title__icontains=strval) 
            query.add(Q(description__icontains=strval), Q.OR)            
            objects = Coll.objects.filter(query).select_related().order_by('-title')[:10]
        else :
            objects = Coll.objects.all().order_by('-title')[:10]

        # for obj in objects:
        #     obj.natural_updated = naturaltime(obj.updated_at)

        favorites = list()
        if request.user.is_authenticated:
            rows = request.user.favorite_colls.values('id')
            favorites = [ row['id'] for row in rows ]

        ctx = {'coll_list' : objects, 'favorites': favorites,'search':strval}
        retval = render(request, self.template_name, ctx)

        dump_queries()
        return retval

class CollDetailView(OwnerDetailView):
    model = Coll
    template_name = "colls/coll_detail.html"
    def get(self, request, pk) :
        x = Coll.objects.get(id=pk)
        comments = Comment.objects.filter(coll=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'coll' : x, 'comments': comments, 'comment_form': comment_form }
        return render(request, self.template_name, context)


class CollCreateView(LoginRequiredMixin, View):
    template_name = 'colls/coll_form.html'
    success_url = reverse_lazy('colls:all')

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)


        coll = form.save(commit=False)
        coll.owner = self.request.user
        coll.save()

        form.save_m2m()
        return redirect(self.success_url)


class CollUpdateView(LoginRequiredMixin, View):
    template_name = 'colls/coll_form.html'
    success_url = reverse_lazy('colls:all')

    def get(self, request, pk):
        coll = get_object_or_404(Coll, id=pk, owner=self.request.user)
        form = CreateForm(instance=coll)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        coll = get_object_or_404(Coll, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=coll)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        coll = form.save(commit=False)
        coll.save()

        return redirect(self.success_url)

class CollDeleteView(OwnerDeleteView):
    model = Coll

def stream_file(request, pk):
    coll = get_object_or_404(Coll, id=pk)
    response = HttpResponse()
    response['Content-Type'] = coll.content_type
    response['Content-Length'] = len(coll.picture)
    response.write(coll.picture)
    return response



class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        coll = get_object_or_404(Coll, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, coll=coll)
        comment.save()
        return redirect(reverse('colls:coll_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "colls/coll_comment_delete.html"

    def get_success_url(self):
        coll = self.object.coll
        return reverse('colls:coll_detail', args=[coll.id])


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Coll, id=pk)
        fav = Fav(user=request.user, coll=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Coll, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, coll=t).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()
import gensim
import time
import csv
from nltk.stem import WordNetLemmatizer, SnowballStemmer

dic = gensim.corpora.Dictionary.load("dict_5436_2021-12-08")
stemmer = SnowballStemmer('english')

customized_stopwords = []

def lemmatize_stemming(text):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

with open('stopwords.csv') as file:
    reader = csv.reader(file)
    for line in reader:
        gensim.utils.simple_preprocess(line[0])
        for sw in gensim.utils.simple_preprocess(line[0]):
            customized_stopwords.append(lemmatize_stemming(sw))

def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and lemmatize_stemming(token) not in customized_stopwords and len(token) > 3:
            result.append(lemmatize_stemming(token))
    return result

def myLda(text):
    lda_model = gensim.models.LdaModel.load("lda5.model")

    myScores = []
    unseen_document = text
    # with open("sample.txt", 'a') as file:
    bow_vector = dic.doc2bow(preprocess(unseen_document))
    # time.sleep(5)
    for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1 * tup[1]):
        # file.write("\n Score: {}\t Topic: {}\n".format(score, lda_model.print_topic(index, 5)))
        print("Score: {}\t Topic: {}".format(score, lda_model.print_topic(index, 5)))
        myScores.append("\n Score: {}\t Topic: {}\n".format(score, lda_model.print_topic(index, 5)))
        if len(myScores) == 3:
            return myScores
    return myScores or []
    # return myScores


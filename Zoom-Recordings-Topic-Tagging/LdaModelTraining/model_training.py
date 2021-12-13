import pandas as pd
import gensim
from nltk.stem import WordNetLemmatizer, SnowballStemmer
import numpy as np
import datetime
import openpyxl as xl
import main
np.random.seed(3219)


data = pd.read_csv('ZoomRecordingsData.csv');
data = data.dropna(subset=['aws_transcript'])
data_text = data[['aws_transcript']]
data_text['index'] = data_text.index
documents = data_text

N = len(documents)

print(len(documents))

stemmer = SnowballStemmer('english')

processed_docs = documents['aws_transcript'].map(main.preprocess)

print(processed_docs)

dic = gensim.corpora.Dictionary(processed_docs)
dic.filter_extremes(no_below=15, no_above=0.5, keep_n=100000) # keep all
dic.save("dict_"+str(N)+"_"+datetime.date.today().strftime("%Y-%m-%d"))

# bag of words
bow_corpus = [dic.doc2bow(doc) for doc in processed_docs]

if __name__ == '__main__':
    # Training
    lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=30, id2word=dic, passes=2, workers=2)
    # Need to have empty excel sheets 'lda-topics' under same directory
    wb = xl.load_workbook("lda-topics.xlsx")
    ws = wb.active
    for idx, topic in lda_model.print_topics(-1):
        print('Topic: {} \nWords: {}'.format(idx, topic))
        ws.append([f'Topic: {idx}', f'Words: {topic}'])

    wb.save("lda-topics.xlsx")
    wb.close()
    lda_model.save('lda5.model')

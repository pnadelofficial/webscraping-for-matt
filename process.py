import pandas as pd
import spacy
import nltk
from sentiment_analysis_spanish import sentiment_analysis
import glob
import sys

import warnings
warnings.filterwarnings("ignore")

DFs = []
for file in list(glob.glob('raw_data/*.csv')):
    DFs.append(pd.read_csv(file))
total = pd.concat(DFs)

nlp = spacy.load("es_core_news_lg")
sentiment = sentiment_analysis.SentimentAnalysisSpanish()

def find_relevant_sents(nlp, df, query):
    nlp_query = nlp(query)
    df['spacy_hl'] = df['headline'].apply(nlp) ## df must have column called 'headline'
    df['hl_sim_score'] = df['spacy_hl'].apply(lambda x: x.similarity(nlp_query))

    threshold = round(df.sort_values('hl_sim_score',ascending=False).iloc[0].hl_sim_score - .2,1)
    sample = df.loc[df['hl_sim_score'] > threshold]
    sample.to_csv(f'query_data/{query}.csv',index=False)
    return sample

def find_relevant_sents_with_sim_score(nlp, df, query, threshold=.5):
    nlp_query = nlp(query)
    df['spacy_hl'] = df['headline'].apply(nlp) ## df must have column called 'headline'
    df['hl_sim_score'] = df['spacy_hl'].apply(lambda x: x.similarity(nlp_query))

    sample = df.loc[df['hl_sim_score'] > threshold]
    sample['sents'] = sample['article_text'].apply(nltk.sent_tokenize)
    sample_explode = sample.explode('sents')

    sample_explode['spacy_sents'] = sample_explode['sents'].apply(nlp)
    sample_explode['sent_sim_score'] = sample_explode['spacy_sents'].apply(lambda x: x.similarity(nlp_query))
    sample_for_sentiment = sample_explode.loc[sample_explode['sent_sim_score'] > threshold]

    sample_for_sentiment['sentiment_score'] = sample_for_sentiment['sents'].apply(sentiment.sentiment)
    
    sample_for_sentiment = sample_for_sentiment[['sents','headline','sentiment_score']]
    sample_for_sentiment.to_csv(f'query_data/{query}_sent_score.csv',index=False)
    return sample_for_sentiment

if len(sys.argv) > 2:
    find_relevant_sents_with_sim_score(nlp,total,sys.argv[1])
else:
    find_relevant_sents(nlp,total,sys.argv[1])
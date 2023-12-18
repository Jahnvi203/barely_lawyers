import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from nltk.corpus import stopwords

def suggest_advice(new_case_fact, threshold=0.15):
    # Load the dataset
    df = pd.read_csv('legal_data.csv')
    
    # Clean the dataset
    df = df.dropna()
    
    # Define stop words
    stop_words = set(stopwords.words('english'))
    stop_words.add('Applicant') 
    stop_words.add('maintenance')

    # Remove stop words from case facts and subtype
    df['Case Facts'] = df['Case Facts'].apply(lambda x: ' '.join([word for word in x.split() if word.lower() not in stop_words]))
    df['Sub-case Type'] = df['Sub-case Type'].apply(lambda x: ' '.join([word for word in x.split() if word.lower() not in stop_words]))
    
    # Concatenate case facts and subtype
    df['Text'] = df['Case Facts'] + ' ' + df['Sub-case Type']

    # Transform the text into numerical vectors
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(df['Text'])

    # Transform the new case into a vector
    new_vector = vectorizer.transform([new_case_fact])

    # Compute the cosine similarity between the new vector and the past vectors
    similarities = cosine_similarity(new_vector, vectors)

    # Get the indices of the past cases with similarity score above the threshold
    similar_indices = similarities.argsort()[0][::-1]
    top_indices = [i for i in similar_indices if similarities[0][i] >= threshold][:3]

    # Get the corresponding case facts and advice for the top similar case facts
    top_case_facts = list(df.iloc[top_indices]['Case Facts'])
    # top_subcase_type = list(df.iloc[top_indices]['Sub-case Type'])
    top_advice = list(df.iloc[top_indices]['Advice'])

    # Return the top similar case facts and advice
    return top_case_facts, top_advice
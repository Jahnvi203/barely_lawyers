import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def suggest_advice(new_case_fact):
    # Load the dataset
    df = pd.read_csv('legal_data.csv')
    
    # Clean the dataset
    df = df.dropna()

    # Transform the case facts into numerical vectors
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(df['Case Facts'])

    # Transform the new case into a vector
    new_vector = vectorizer.transform([new_case_fact])

    # Compute the cosine similarity between the new vector and the past vectors
    similarities = cosine_similarity(new_vector, vectors)

    # Get the indices of the top 3 most similar legal issues
    similar_indices = similarities.argsort()[0][-3:]
    print(similar_indices)

    # Get the corresponding case facts and advice for the top 3 most similar case facts
    top_case_facts = list(df.iloc[similar_indices]['Case Facts'])
    top_advice = list(df.iloc[similar_indices]['Advice'])

    # Return the top 3 advice
    return top_case_facts, top_advice
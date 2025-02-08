from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def detect_contradictions(clauses):
    contradiction_pairs = []
    texts = [c['text'] for c in clauses]

    vectorizer = TfidfVectorizer().fit_transform(texts)
    vectors = vectorizer.toarray()

    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            sim_score = cosine_similarity([vectors[i]], [vectors[j]])[0][0]
            if sim_score < 0.3:  # Low similarity means potential contradiction
                contradiction_pairs.append({"clause_1": texts[i], "clause_2": texts[j]})

    return contradiction_pairs

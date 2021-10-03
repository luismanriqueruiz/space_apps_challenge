# Developed by: Eliana Corredor Caro and Carlos Manrique

# This file loads results from subjects SKOS file, analyze clusters by using K-means.
# Several trials where done to find the appropriate number of clusters but further investigation must be done for the corpus.
# These clusters are plotted into a 2D chart by reducing the dimensions (MultiDimensional scaling).
# Finally, this script generates most common terms between texts while dropping stop words.

# Environment: base - conda


#%%
from rdfpandas.graph import to_dataframe
import pandas as pd
from rdflib import Graph
import re
import matplotlib.pyplot as plt
from sklearn.manifold import MDS

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

from nltk.corpus import stopwords
stop = stopwords.words('english')

# removing specific words
stop = stop + ['space']

pd.set_option('max_columns', None)
pd.set_option('max_rows', None)


#%%
g = Graph()
folder = "./Documents/Research/nasa/ontologies/sources/taxonomy/files/"

g.parse(folder + 'subjects.skos', format = 'xml', encoding="ISO-8859-1")
df = to_dataframe(g)

# %%
df.head()


# %%
df.iloc[10]

# %%
# Analyzing literal
colLiteral = df.columns[df.columns.str.contains('altLabel')].tolist()

#%%
df_Literal = df[colLiteral]
df_Literal = df_Literal.fillna('')
df_Literal['all'] = df_Literal.agg(' '.join, axis=1)
df_Literal['all'] = df_Literal['all'].apply(lambda x: re.sub('[^A-Za-z]+', ' ', x))

# Removing stop words
df_Literal['all_stopwords'] = df_Literal['all'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))



#%%
df_Literal['all_stopwords'].head()



# %%
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df_Literal['all_stopwords'].tolist())
a = vectorizer.get_feature_names()



#%%
dist = 1 - cosine_similarity(X)
dist


#%%
#pd.DataFrame(a).to_csv('uniquewords.csv', index=False)

#%%
result = pd.DataFrame(data=X.toarray(), columns=vectorizer.get_feature_names())

plt.figure(figsize=(14, 7))
result.sum(axis=0).sort_values(ascending=False)[0:50].plot.bar()


#%%
# K-means

num_clusters = 5
km = KMeans(n_clusters=num_clusters)
km.fit(X)
clusters = km.labels_.tolist()
clusters


#%%
unique_clusters = list(set(clusters))
print(unique_clusters)



#%%
# Multidimensional scale

# convert two components as we're plotting points in a two-dimensional plane
mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1)

pos = mds.fit_transform(dist)  # shape (n_components, n_samples)
xs, ys = pos[:, 0], pos[:, 1]


# %%
df_results = pd.DataFrame(dict(x=xs, y=ys, label=clusters))
display(df_results.head())
df_results['label'].value_counts()


#%%
for i in unique_clusters:
	print('cluster:', str(i))
	tmp = result.iloc[df_results[df_results.label == i].index, :]
	print(tmp.sum(axis=0).sort_values(ascending=False)[0:6])


# %%
groups = df_results.groupby('label')

for name, group in groups:
	plt.plot(group.x, group.y, marker='o', linestyle='', markersize=12, label=name)
plt.legend()

# %%

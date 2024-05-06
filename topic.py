from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
import json
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

# Open the JSON file
with open('react_stackoverflow.json', 'r') as file:
    # Load JSON data into a dictionary
    data = json.load(file)

docs = [question['title'] + ' ' + question['body'] for question in data]
print(len(docs))

docs_small = docs[:3000]

zeroshot_topic_list = ["Performance",
                       "State Management",
                       "Component Architecture",
                       "Rendering Optimization",
                       "Dependency Management",
                       "API Design",
                       "Tooling and Development Experience",
                       "Accessibility",
                       "Browser Compatibility",
                       "Community and Ecosystem",
                       ]


# zeroshot_topic_list = [
#     "Rendering Performance",
#     "Memory Management",
#     "State Complexity",
#     "Global State Management",
#     "Component Composition",
#     "Component Reusability",
#     "Virtual DOM",
#     "Server-side Rendering - SSR",
#     "Dependency Graph",
#     "Package Management",
#     "API Consistency and Clarity",
#     "API Stability",
#     "Accessibility Features",
#     "Cross-browser Compatibility",
#     "Community Support",
#     "Ecosystem Diversity"
# ]

filtered_texts = []
# for text in docs_small:
#     # Tokenize the text into words
#     words = nltk.word_tokenize(text)
    
#     # Remove stopwords from the text
#     filtered_text = [word for word in words if word.lower() not in stop_words]
    
#     # Join the filtered words back into a sentence
#     filtered_sentence = ' '.join(filtered_text)
    
#     # Append the filtered text to the list
#     filtered_texts.append(filtered_sentence)

topic_model = BERTopic(
    embedding_model="thenlper/gte-small", 
    min_topic_size=15,
    zeroshot_topic_list=zeroshot_topic_list,
    zeroshot_min_similarity=.85,
    representation_model=KeyBERTInspired()
)
topics, _ = topic_model.fit_transform(docs_small)

print(topic_model.get_topic_info())
print(topic_model.get_topic(0))
print(topic_model.get_document_info(docs_small))
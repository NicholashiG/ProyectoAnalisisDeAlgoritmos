import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

class TextPreprocessor:
    """Clase para preprocesar abstracts científicos."""
    
    def __init__(self):
        """Inicializa el preprocesador con recursos NLTK necesarios."""
        # Descargar recursos NLTK necesarios
        print("Descargando recursos NLTK necesarios...")
        try:
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
            print("Recursos NLTK descargados correctamente")
        except Exception as e:
            print(f"Error al descargar recursos NLTK: {e}")
            print("Continuando con funcionalidad limitada...")
        
        # Inicializar recursos
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            print("Error al cargar stopwords, usando una lista básica")
            self.stop_words = {"a", "an", "the", "and", "or", "but", "if", "because", 
                              "as", "what", "which", "this", "that", "these", "those", 
                              "then", "just", "so", "than", "such", "both", "through", 
                              "about", "for", "is", "of", "while", "during", "to", "in", "on"}
        
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
    
    def clean_text(self, text):
        """Limpia el texto eliminando puntuación y caracteres especiales."""
        if not isinstance(text, str):
            return ""
        
        # Convertir a minúsculas
        text = text.lower()
        
        # Eliminar puntuación
        text = re.sub(f'[{string.punctuation}]', ' ', text)
        
        # Eliminar números
        text = re.sub(r'\d+', ' ', text)
        
        # Eliminar espacios múltiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize_safely(self, text):
        """Tokeniza el texto de forma segura."""
        # Intentar usar word_tokenize de NLTK
        try:
            return word_tokenize(text)
        except:
            # Si falla, usar una tokenización simple por espacios
            return text.split()
    
    def remove_stopwords(self, text):
        """Elimina stopwords del texto."""
        tokens = self.tokenize_safely(text)
        filtered_tokens = [word for word in tokens if word not in self.stop_words]
        return ' '.join(filtered_tokens)
    
    def stem_text(self, text):
        """Aplica stemming al texto."""
        tokens = self.tokenize_safely(text)
        stemmed_tokens = [self.stemmer.stem(word) for word in tokens]
        return ' '.join(stemmed_tokens)
    
    def lemmatize_text(self, text):
        """Aplica lematización al texto."""
        tokens = self.tokenize_safely(text)
        lemmatized_tokens = [self.lemmatizer.lemmatize(word) for word in tokens]
        return ' '.join(lemmatized_tokens)
    
    def preprocess(self, text, use_stemming=True):
        """Realiza el preprocesamiento completo del texto."""
        cleaned_text = self.clean_text(text)
        no_stopwords = self.remove_stopwords(cleaned_text)
        
        if use_stemming:
            return self.stem_text(no_stopwords)
        else:
            return self.lemmatize_text(no_stopwords)
    
    def vectorize_corpus(self, corpus):
        """Convierte una colección de textos a vectores TF-IDF."""
        vectorizer = TfidfVectorizer(max_features=1000)
        return vectorizer.fit_transform(corpus)
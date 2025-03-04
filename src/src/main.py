# FILE: /ProyectoAnalisisDeAlgoritmos/src/main.py
import os
from data_processing import load_and_clean_data
from analysis import generate_statistics, measure_textual_similarity
from visualization import visualize_results

def main():
    # Define paths for raw and processed data
    raw_data_path = os.path.join('data', 'raw')
    processed_data_path = os.path.join('data', 'processed')

    # Load and clean data
    cleaned_data = load_and_clean_data(raw_data_path)

    # Generate statistics
    statistics = generate_statistics(cleaned_data)

    # Measure textual similarity
    similarity_results = measure_textual_similarity(cleaned_data)

    # Visualize results
    visualize_results(statistics, similarity_results)

if __name__ == "__main__":
    main()
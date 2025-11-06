"""
Test script to make predictions on real data

Run this to test the model with your actual network traffic data.
"""

import joblib
import pandas as pd
import os
import numpy as np

def load_model():
    """Load the trained model"""
    # Try different model paths
    model_paths = [
        'ai-model/saved_models/dvwa_attack_detector_top20.pkl',
        'ai-model/saved_models/dvwa_attack_detector.pkl',
        'ai-model/saved_models/rf_model.pkl',
        'ai-model/saved_models/attack_detector.pkl'
    ]
    
    for model_path in model_paths:
        if os.path.exists(model_path):
            print(f"✓ Loading model: {model_path}")
            model = joblib.load(model_path)
            return model, model_path
    
    print("❌ No model found! Please train it first:")
    print("   python ai-model/train_model.py")
    return None, None

def test_real_data():
    """Test the model with real network traffic data"""
    
    model, model_path = load_model()
    if model is None:
        return
    
    # Load the processed data
    data_path = 'ai-model/final_top20_features.csv'
    if not os.path.exists(data_path):
        print(f"❌ Data file not found: {data_path}")
        print("Please run the feature extraction pipeline first.")
        return
    
    print(f"✓ Loading data: {data_path}")
    df = pd.read_csv(data_path)
    
    print("="*70)
    print("TESTING AI MODEL WITH REAL NETWORK TRAFFIC DATA")
    print("="*70)
    print(f"\nDataset: {df.shape[0]} flows with {df.shape[1]} features")
    print(f"Model: {os.path.basename(model_path)}")
    
    # Make predictions
    print("\n🔮 Making predictions...")
    predictions = model.predict(df)
    
    # Get prediction probabilities if available
    try:
        probabilities = model.predict_proba(df)
        has_proba = True
    except:
        has_proba = False
    
    # Analyze predictions
    unique, counts = np.unique(predictions, return_counts=True)
    
    print("\n" + "="*70)
    print("PREDICTION SUMMARY")
    print("="*70)
    
    for label, count in zip(unique, counts):
        percentage = (count / len(predictions)) * 100
        bar = '█' * int(percentage / 2)
        print(f"  Class {label}: {count:4d} flows ({percentage:5.1f}%) {bar}")
    
    # Show detailed stats
    print("\n" + "="*70)
    print("DETAILED STATISTICS")
    print("="*70)
    
    for label in unique:
        mask = predictions == label
        count = np.sum(mask)
        
        print(f"\n📊 Class {label} ({count} flows):")
        
        if has_proba:
            avg_confidence = np.mean(np.max(probabilities[mask], axis=1))
            print(f"   Average confidence: {avg_confidence:.2%}")
        
        # Show some sample feature statistics for this class
        class_data = df[mask]
        print(f"   Sample feature means:")
        for col in df.columns[:5]:  # Show first 5 features
            print(f"     {col}: {class_data[col].mean():.2f}")
    
    # Show some individual predictions
    print("\n" + "="*70)
    print("SAMPLE PREDICTIONS (First 10 flows)")
    print("="*70)
    
    for i in range(min(10, len(df))):
        pred = predictions[i]
        print(f"\nFlow #{i+1}: Predicted Class = {pred}")
        
        if has_proba:
            proba = probabilities[i]
            print(f"  Confidence: {np.max(proba):.2%}")
            print(f"  Class probabilities: {proba}")
    
    # Save predictions
    output_path = 'ai-model/predictions_output.csv'
    df['prediction'] = predictions
    if has_proba:
        for i in range(probabilities.shape[1]):
            df[f'prob_class_{i}'] = probabilities[:, i]
    
    df.to_csv(output_path, index=False)
    print("\n" + "="*70)
    print(f"✅ Predictions saved to: {output_path}")
    print("="*70)

if __name__ == "__main__":
    test_real_data()

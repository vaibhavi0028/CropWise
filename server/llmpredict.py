
# 3. Interactive CLI for asking questions
def interactive_cli(model_path="Model2/llm"):
    """Interactive command-line interface for asking questions to the model"""
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load tokenizer and model
    try:
        print(f"Loading model from {model_path}...")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(device)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    print("\n=== Agricultural Assistant ===")
    print("Type 'exit' to end the conversation")
    
    while True:
        question = input("\nAsk a question about agriculture: ")
        if question.lower() in ['exit', 'quit', 'bye']:
            print("Thank you for using the Agricultural Assistant. Goodbye!")
            break
            
        # Prepare input
        input_text = "agriculture question: " + question
        input_ids = tokenizer.encode(input_text, return_tensors="pt").to(device)
        
        # Generate answer
        with torch.no_grad():
            outputs = model.generate(
                input_ids=input_ids,
                max_length=300,
                min_length=10,
                num_beams=4,
                no_repeat_ngram_size=2,
                early_stopping=True,
                temperature=0.8,
            )
        
        # Decode and print answer
        answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Fallback for empty answers
        if not answer or answer.isspace():
            answer = "I'm sorry, I don't have enough information to answer that question."
        
        print(f"Assistant: {answer}")

# Example usage for interactive CLI:
interactive_cli(model_path="Model2/llm")
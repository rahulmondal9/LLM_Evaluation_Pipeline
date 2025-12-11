import json
from pathlib import Path
from evaluator import Evaluator

# Setup folders
DATA_DIR = Path("data")
REPORTS_DIR = DATA_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def load_json(filename):
    """Helper to load a JSON file safely."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_text_data(chat_json, context_json):
    """
    Digs into the JSONs to find just the strings we need.
    """
    # 1. Get Chat info (Last User query + Last AI response)
    user_msg = ""
    ai_msg = ""
    for turn in chat_json.get("conversation_turns", []):
        if turn['role'] == 'User':
            user_msg = turn['message']
        elif turn['role'] == 'AI/Chatbot':
            ai_msg = turn['message']
            
    # 2. Get Context info (All text chunks)
    context_texts = []
    vector_data = context_json.get("data", {}).get("vector_data", [])
    for item in vector_data:
        if item.get("text"):
            context_texts.append(item['text'])
            
    return user_msg, ai_msg, context_texts

def print_pretty_report(results):
    """
    Prints the evaluation in a human-readable format.
    """
    print("\n" + "="*60)
    print("EVALUATION RESULTS SUMMARY")
    print("="*60)
    
    # 1. Relevance
    rel = results['relevance_score'] * 100
    rel_status = "Good" if rel > 70 else "Fair" if rel > 50 else "Poor"
    print(f"Relevance Score:   {rel:.1f}% - {rel_status} alignment with user query")
    
    # 2. Completeness
    comp = results['completeness_score'] * 100
    comp_status = "High" if comp > 80 else "Good" if comp > 60 else "Low"
    print(f"Completeness Score: {comp:.1f}% - {comp_status} coverage of context")
    
    # 3. Hallucination
    hall = results['hallucination']['summary']
    bad_sents = hall['unsupported_count']
    total_sents = hall['total_sentences']
    ratio = hall['unsupported_ratio'] * 100
    print(f"Hallucination Check: {bad_sents} out of {total_sents} sentences flagged as potentially unsupported ({ratio:.0f}%)")
    
    # 4. Metrics
    metrics = results['metrics']
    print(f"Latency:            {metrics['latency']:.3f} seconds")
    print(f"Cost:               ${metrics['cost_usd']:.6f} USD")
    print("="*60 + "\n")

def main():
    # Find all chat files in the data folder
    chat_files = sorted(DATA_DIR.glob("sample-chat-conversation-*.json"))
    
    if not chat_files:
        print("No files found! Did you run setup_data.py?")
        return

    for chat_file in chat_files:
        # Find the matching context file (e.g., 01 matches 01)
        # To assume the file ends in "-01.json" or "-02.json"
        file_id = chat_file.stem.split("-")[-1] 
        context_file = DATA_DIR / f"sample_context_vectors-{file_id}.json"
        
        if not context_file.exists():
            print(f"Skipping {chat_file.name} (Context file missing)")
            continue
            
        print(f"Processing Pair: {chat_file.name} <-> {context_file.name}")
        
        # Load and Extract
        chat_data = load_json(chat_file)
        context_data = load_json(context_file)
        user_msg, ai_msg, context_texts = extract_text_data(chat_data, context_data)
        
        # Run Evaluation
        evaluator = Evaluator(context_texts, user_msg, ai_msg)
        results = evaluator.evaluate()
        
        # Save Report
        report_path = REPORTS_DIR / f"{chat_file.name}.report.json"
        with open(report_path, "w", encoding='utf-8') as f:
            json.dump(results, f, indent=2)
            
        # Show Output
        print_pretty_report(results)

if __name__ == "__main__":
    main()
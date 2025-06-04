from agents.offer_negotiation.agent import run_agent

def main():
    # Test input
    test_input = {"deal_id": "LOCAL123"}
    
    print("\n=== Starting Agent Test ===")
    print(f"Input: {test_input}\n")
    
    # Run the agent
    result = run_agent(test_input)
    
    print("\n=== Final Result ===")
    print(f"Output: {result}")

if __name__ == "__main__":
    main()

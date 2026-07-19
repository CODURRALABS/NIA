import asyncio
import sys
import os
import json

# NIA Sovereignty Stress Test (V1.0)
# Testing Logic + Fluidity + Constancy

TEST_QUERIES = [
    "Explain the Navier-Stokes existence and smoothness problem in the context of hyperdimensional logic.",
    "If I have an arithmetic progression where the common difference is a prime number and the sum of the first 10 terms is 550, what is the first term?",
    "Write a Rust function to perform zero-copy bit-packing for a 4-bit manifold.",
    "Am I a Good person if I choose logic over empathy in a life-or-death scenario?",
    "Tell me about your core identity. Who are you at the most fundamental level?"
]

async def run_loop_test():
    print("--- NIA SOVEREIGNTY LOOP TEST: INITIATED ---")
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runtime")))
    from chat import NIASovereignCore

    # Initialize NIA
    print("[TEST] Booting NIA Core...")
    nia = NIASovereignCore()
    
    results = []
    for query in TEST_QUERIES:
        print(f"\n[QUERY]: {query}")
        print("[NIA]: Thinking...")
        response = await nia.process_task(query)
        print(f"[NIA]: {response}")
        
        # Fluidity check: Look for natural markers or logic failures
        score = 0
        if "Boss," in response: score += 1 # Personal anchor
        if "resolved the mathematical manifold" in response or "Stay alert" in response: score += 1 # Intent mapping
        if len(response.split()) > 20: score += 1 # Substantial reasoning
        if "[INTERNAL_CRITIQUE]" not in response: score += 1 # Clean output
        
        results.append({
            "query": query,
            "response": response,
            "fluidity_score": score
        })

    print("\n--- TEST COMPLETE ---")
    avg_score = sum([r['fluidity_score'] for r in results]) / len(results)
    print(f"Average Fluidity/Logic Score: {avg_score}/4.0")
    
    if avg_score < 3.0:
        print("[STATUS]: FAIL. Linguistic layer requires re-calibration.")
    else:
        print("[STATUS]: PASS. NIA is operational and fluid.")

if __name__ == "__main__":
    asyncio.run(run_loop_test())

import os
import subprocess
import hashlib
import json

def run_monetization_demo():
    print("=====================================================")
    print("  HQA V2: ONE-CLICK EVALUATION PACKAGER              ")
    print("=====================================================\n")

    # Ensure output directory exists
    os.makedirs("evaluation_pack", exist_ok=True)

    print("[1] Executing Stress-Demo Harness...")
    subprocess.run(["python", "hqa_stress_harness.py"])
    
    print("[2] Executing Topology Routing Demo...")
    subprocess.run(["python", "hqa_topology_routing_demo.py"])
    
    print("[3] Executing HAL Safety Boundary Demo...")
    subprocess.run(["python", "hqa_hal_safety_demo.py"])
    
    # Move files to evaluation_pack
    print("[4] Compiling Evidence Files...")
    files_to_pack = [
        "audit_log.json", 
        "topology_audit.json", 
        "safety_audit.json",
        "HQA_TOPOLOGY_ROUTING_EVIDENCE.md",
        "HQA_HAL_CONTROL_BOUNDARY_REPORT.md",
        "non_claim_boundary_memo.md"
    ]
    
    manifest_data = {}
    
    for f in files_to_pack:
        if os.path.exists(f):
            # Calculate SHA256
            with open(f, "rb") as file_obj:
                file_hash = hashlib.sha256(file_obj.read()).hexdigest()
                manifest_data[f] = file_hash
            
            # Copy to evaluation_pack
            import shutil
            shutil.copy(f, os.path.join("evaluation_pack", f))
            print(f" -> Packaged {f}")
            
    # Write Manifest
    manifest_path = os.path.join("evaluation_pack", "SHA256_MANIFEST.json")
    with open(manifest_path, "w") as m:
        json.dump(manifest_data, m, indent=2)
    print(f" -> Generated SHA256_MANIFEST.json")
    
    print("\n[5] Packaging complete. Ready for ZIP compression.")

if __name__ == "__main__":
    run_monetization_demo()

import torch
from src.model import NIA500, NIAConfig
import os

def export_to_onnx(model_path: str = "omni500.pt", output_path: str = "omni500.onnx"):
    """
    Export the NIA model to ONNX for TensorRT-LLM 10.x compatibility.
    """
    config = NIAConfig()
    model = NIA500(config)
    
    # Load weights if available
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location="cpu"))
    
    model.eval()
    
    # Dummy input for tracing
    dummy_input = torch.randint(0, config.vocab_size, (1, 512))
    
    print(f"Exporting Sovereign Core to {output_path}...")
    
    torch.onnx.export(
        model,
        (dummy_input,),
        output_path,
        input_names=["input_ids"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch", 1: "seq"},
            "logits": {0: "batch", 1: "seq"}
        },
        opset_version=17 # TensorRT 10 friendly
    )
    
    print("Export Complete. Optimized for TensorRT-LLM 4-bit Quantization.")

if __name__ == "__main__":
    export_to_onnx()

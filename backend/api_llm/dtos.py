from dataclasses import dataclass
import torch
from typing import Optional, Any


@dataclass
class GenerationContext:
    """
    Encapsulates the metrics and tensors obtained during the generation
    process for a single prompt sequence.

    Attributes:
        input_ids_seq (torch.Tensor): The tokenized input sequence.
        padded_input_len (int): The length of the padded input sequence.
        prompt_tokens_count (int): The actual number of tokens in the prompt (excluding padding).
        raw_output_seq (torch.Tensor): The raw generated sequence from the model.
        seq_scores (Optional[torch.Tensor]): The transition scores (logits) for the generated sequence.
        avg_latency (float): The generation latency in seconds.
        peak_memory_mb (float): The peak GPU memory consumption during generation in MB.
        is_encoder_decoder (bool): Indicates if the model uses an encoder-decoder architecture.
    """
    input_ids_seq: torch.Tensor
    padded_input_len: int
    prompt_tokens_count: int
    raw_output_seq: torch.Tensor
    seq_scores: Optional[torch.Tensor]
    avg_latency: float
    peak_memory_mb: float
    is_encoder_decoder: bool


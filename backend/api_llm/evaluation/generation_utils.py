import torch
from transformers import PreTrainedTokenizerFast


def extract_clean_generated_text(
        tokenizer: PreTrainedTokenizerFast,
        raw_sequence: torch.Tensor,
        prompt_length: int,
        is_encoder_decoder: bool,
        clean_prompt: str
) -> tuple[str, int]:
    """
    Slices the generated sequence based on architecture, decodes it,
    and securely strips any echoed prompts.

    Args:
        tokenizer: The tokenizer used to decode the output.
        raw_sequence: The raw sequence tensor from model.generate().
        prompt_length: The length of the input tokens.
        is_encoder_decoder: True if the model is Encoder-Decoder (e.g., T5).
        clean_prompt: The plain text prompt used for fallback cleanup.

    Returns:
        tuple[str, int]: A tuple containing the clean generated text and the number of generated tokens.
    """
    if is_encoder_decoder:
        generated_sequence = raw_sequence
    else:
        generated_sequence = raw_sequence[prompt_length:]

    generated_text = tokenizer.decode(generated_sequence, skip_special_tokens=True)

    if clean_prompt and generated_text.startswith(clean_prompt):
        generated_text = generated_text[len(clean_prompt):].strip()

    return generated_text.strip(), len(generated_sequence)

import json
import keras
import tf_keras


def adapt_config_for_keras3(config: dict | list) -> dict | list:
    """
    Recursively sanitizes and adapts the JSON configuration for native Keras 3 compatibility.

    This function dynamically renames the legacy 'Model' class name to 'Functional'
    and safely removes deprecated parameters such as 'data_format' from specific
    preprocessing layers. It also ensures that 'input_layers' and 'output_layers'
    are properly formatted as nested lists, which is strictly required by Keras 3.

    Args:
        config (dict | list): The model configuration dictionary or list.

    Returns:
        dict | list: The adapted configuration object for Keras 3.
    """
    keys_to_remove = ['quantization_config', 'optional', 'ragged', 'sparse', 'is_legacy_layer']
    preprocessing_layers = ['RandomFlip', 'RandomRotation', 'RandomZoom', 'RandomCrop', 'RandomTranslation']

    if isinstance(config, dict):
        if config.get("class_name") == "Model":
            config["class_name"] = "Functional"

        if config.get("class_name") in preprocessing_layers:
            layer_config = config.get("config")
            if isinstance(layer_config, dict):
                layer_config.pop("data_format", None)

        if "input_layers" in config:
            if isinstance(config["input_layers"], list) and len(config["input_layers"]) > 0 and isinstance(config["input_layers"][0], str):
                config["input_layers"] = [config["input_layers"]]

        if "output_layers" in config:
            if isinstance(config["output_layers"], list) and len(config["output_layers"]) > 0 and isinstance(config["output_layers"][0], str):
                config["output_layers"] = [config["output_layers"]]

        for key in keys_to_remove:
            config.pop(key, None)

        for key, value in list(config.items()):
            config[key] = adapt_config_for_keras3(value)

    elif isinstance(config, list):
        config = [adapt_config_for_keras3(item) for item in config]

    return config


def clean_keras2_config(config: dict | list) -> dict | list:
    """
    Recursively sanitizes and adapts the JSON configuration for tf_keras (Keras 2) compatibility.

    This function ensures older architectures map parameter names correctly (e.g., 'batch_shape')
    and strips incompatible arguments from legacy data augmentation layers.

    Args:
        config (dict | list): The model configuration dictionary or list.

    Returns:
        dict | list: The adapted configuration object for legacy Keras 2.
    """
    keys_to_remove = ['quantization_config', 'optional', 'ragged', 'sparse', 'is_legacy_layer']
    preprocessing_layers = ['RandomFlip', 'RandomRotation', 'RandomZoom', 'RandomCrop', 'RandomTranslation']

    if isinstance(config, dict):
        if 'batch_shape' in config:
            config['batch_input_shape'] = config.pop('batch_shape')

        if config.get("class_name") in preprocessing_layers:
            layer_config = config.get("config")
            if isinstance(layer_config, dict):
                layer_config.pop("data_format", None)

        for key in keys_to_remove:
            config.pop(key, None)

        for key, value in list(config.items()):
            config[key] = clean_keras2_config(value)

    elif isinstance(config, list):
        config = [clean_keras2_config(item) for item in config]

    return config


def load_keras_model(arch_path: str, weights_path: str):
    """
    Instantiates a Keras model from a JSON architecture file and loads weights using multiple strategies.

    This pipeline guarantees maximum compatibility across framework versions by trying
    native Keras 3 first, falling back to legacy Keras 2 (tf_keras), and finally
    attempting direct weight loading.

    Args:
        arch_path (str): The file path to the JSON document containing the model's structure.
        weights_path (str): The file path to the file containing the trained weights.

    Returns:
        Model: The fully instantiated model (either keras.Model or tf_keras.Model).

    Raises:
        RuntimeError: If all loading strategies fail.
    """
    loading_errors = []

    with open(arch_path, 'r', encoding='utf-8') as f:
        model_json_string = f.read()

    try:
        config_dict = json.loads(model_json_string)
        cleaned_config_dict_v3 = adapt_config_for_keras3(config_dict)
        model_json_clean_v3 = json.dumps(cleaned_config_dict_v3)

        model = keras.models.model_from_json(model_json_clean_v3)
        model.load_weights(weights_path)
        return model
    except Exception as e:
        loading_errors.append(f"Keras 3 Strategy failed: {str(e)}")

    try:
        config_dict_v2 = json.loads(model_json_string)
        cleaned_config_dict_v2 = clean_keras2_config(config_dict_v2)
        model_json_clean_v2 = json.dumps(cleaned_config_dict_v2)

        model = tf_keras.models.model_from_json(model_json_clean_v2)
        model.load_weights(weights_path)
        return model
    except Exception as e:
        loading_errors.append(f"tf_keras Strategy failed: {str(e)}")

    try:
        model = keras.models.load_model(weights_path, compile=False)
        return model
    except Exception as e:
        loading_errors.append(f"Direct load Strategy failed: {str(e)}")

    raise RuntimeError(f"Critical failure while loading the model. Errors: {loading_errors}")
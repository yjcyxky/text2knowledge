# Text2Knowledge Chatbot

[简体中文](README_CN.md)

## Introduction

Text2Knowledge Chatbot is a chatbot project developed in the Rust programming language. This project focuses on utilizing advanced natural language processing technologies to provide users with text-based knowledge extraction and interactive chatting experiences.

## Installation and Configuration

To run the Text2Knowledge Chatbot locally, please follow these steps:

### Prerequisites

Ensure that you have the Rust programming environment installed on your system. If not installed, please visit the [official Rust website](https://www.rust-lang.org/) and follow the installation guide.

### Clone the Repository

Clone the repository to your local machine with the following command:

```bash
git clone https://github.com/yjcyxky/text2knowledge.git
cd text2knowledge/chatbot
```

### Install Dependencies

The project relies on several external libraries, which can be installed with the following command:

```bash
cargo build
```

## How to Use

After installing all dependencies, you can run the chatbot with the following command:

```bash
cargo run -- --help
```

### Examples

```bash
# Basic usage with default model and prompt
target/release/chatbot --which 7b-mistral

# Custom usage with specified model, tokenizer, and prompt
target/release/chatbot --model path/to/model.bin --tokenizer path/to/tokenizer.json --prompt "Hello, world!"

# Advanced usage with specific parameters
target/release/chatbot --which 7b-mistral --prompt interactive --sample-len 150 --temperature 0.7 --top-p 0.9

# Advanced usage with chat mode
target/release/chatbot --which 7b-mistral --prompt chat --sample-len 150 --temperature 0.7 --top-p 0.9
```

### Models

| Abbr                | Human-readable Abbr [Argument --which]        | Full Model Name                           | Related GGML File                               |
| ------------------- | ------------------- | -------------------------------------- | ------------------------------------ |
| `L7b`               | 7b                  | TheBloke/Llama-2-7B-GGML               | llama-2-7b.ggmlv3.q4_0.bin           |
| `Vicuna13b`         | vicuna13b           | lmsys/vicuna-13b-v1.5-16k              | pytorch_model-00003-of-00003.bin     |
| `L33b`              | 33b                 | TheBloke/vicuna-33B-GGUF               | vicuna-33b.Q5_K_M.gguf               |
| `L33bQ`             | 33bQ                | TheBloke/vicuna-33B-GGUF               | vicuna-33b.Q6_K.gguf                 |
| `L13b`              | 13b                 | TheBloke/Llama-2-13B-GGML              | llama-2-13b.ggmlv3.q4_0.bin          |
| `L70b`              | 70b                 | TheBloke/Llama-2-70B-GGML              | llama-2-70b.ggmlv3.q4_0.bin          |
| `L7bChat`           | 7b-chat             | TheBloke/Llama-2-7B-Chat-GGML          | llama-2-7b-chat.ggmlv3.q4_0.bin      |
| `L13bChat`          | 13b-chat            | TheBloke/Llama-2-13B-Chat-GGML         | llama-2-13b-chat.ggmlv3.q4_0.bin     |
| `L70bChat`          | 70b-chat            | TheBloke/Llama-2-70B-Chat-GGML         | llama-2-70b-chat.ggmlv3.q4_0.bin     |
| `L7bCode`           | 7b-code             | TheBloke/CodeLlama-7B-GGUF             | codellama-7b.Q8_0.gguf               |
| `L13bCode`          | 13b-code            | TheBloke/CodeLlama-13B-GGUF            | codellama-13b.Q8_0.gguf              |
| `L34bCode`          | 32b-code            | TheBloke/CodeLlama-34B-GGUF            | codellama-34b.Q8_0.gguf              |
| `Mistral7b`         | 7b-mistral          | TheBloke/Mistral-7B-v0.1-GGUF          | mistral-7b-v0.1.Q4_K_S.gguf          |
| `Mistral7bInstruct` | 7b-mistral-instruct | TheBloke/Mistral-7B-Instruct-v0.1-GGUF | mistral-7b-instruct-v0.1.Q4_K_S.gguf |


### Command-Line Tool Usage

This tool allows for flexible and customizable text generation based on the specified model and parameters. Below are the available command-line arguments and their descriptions.

Arguments

```
--which: Specifies the model size to use. Default is 7b.
--model: Path to the GGML file (typically a .bin file). If not specified, the model will be downloaded based on the --which argument. If a local path is specified, a matching --which argument must also be provided.
--tokenizer: Path to the tokenizer config in JSON format. If not specified, it will be downloaded based on the --which argument.
--prompt: The initial prompt to use. Can be a specific text, 'interactive' for multiple prompts, or 'chat' for an interactive model with preserved history. Default is 'My favorite theorem is'.
-n, --sample_len: The length of the generated sample in tokens. Default is 100.
--temperature: The temperature used for generating samples. Use 0 for greedy sampling. Default is 0.8.
--top_p: Nucleus sampling probability cutoff.
--seed: The seed used for generating random samples. Default is 299792458.
--tracing: Enable tracing, which generates a trace-timestamp.json file.
--verbose_prompt: Display the token for the specified prompt.
--repeat_penalty: Penalty applied for repeating tokens. 1 means no penalty. Default is 1.1.
--repeat_last_n: The context size considered for the repeat penalty. Default is 64.
--gqa: Group-Query Attention - the number of groups to use. Defaults are 1 for models like L7b, L13b, etc., and 8 for models like Mistral7b, L70b, etc.
```

## Contribution Guidelines

We welcome and appreciate any contributions from the community members. If you wish to contribute to Text2Knowledge Chatbot, please follow these steps:

1. Fork the repository and create your branch.
2. Make changes in your branch.
3. Submit a Pull Request.

Please ensure that your code adheres to the project's coding style and quality standards before submitting your contribution.

## License

Text2Knowledge Chatbot is released under the MIT License. For more details, please refer to the `LICENSE` file in the repository.

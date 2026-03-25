# MeTTa Game – Server

> **Note:** This repository contains the server for MeTTa Game. If you're looking for the client, visit [MeTTa Game – Client](https://github.com/fluidity-labs/metta-game-client).

**MeTTa Game** is a fun and educational text-based RPG that showcases the power of [OpenCog Hyperon](https://hyperon.opencog.org/) and the [MeTTa language](https://metta-lang.dev/). It features a procedurally generated world with advanced reasoning and memory management capabilities. Designed to foster community adoption and engagement, MeTTa Game serves as an interactive way to explore and expand the utility of MeTTa while immersing players in a dynamic AI-driven experience.

The game includes a built-in console where players can observe all actions taken by MeTTa during gameplay, providing transparency into its decision-making and reasoning process. Additionally, an admin mode allows any query or action to be performed, offering deeper exploration and experimentation with MeTTa’s full capabilities.

## Features

- 🌍 **Procedural Generation** – The game world is dynamically created based on AI-driven rules.
- 🧠 **Advanced Reasoning** – Powered by OpenCog Hyperon for intelligent decision-making.
- 📜 **Memory Management** – NPCs and the environment retain and adapt to past interactions.
- 🎮 **Text-Based Adventure** – A rich, interactive experience where players navigate and shape the world through text commands.
- 🖥️ **Action Console** – Players can view all actions taken by MeTTa during gameplay, providing insight into its reasoning process.
- 🔧 **Admin Mode** – Any user can take control and execute any action, allowing for deeper experimentation with MeTTa's capabilities.

## Getting Started

### Prerequisites
- **Python 3.8+**  
- **pip** (Python package manager)
- **Linux/macOS** (Hyperon is currently not available on Windows)
- [**MeTTa Game – Client**](https://github.com/fluidity-labs/metta-game-client)

### Installation

```sh
# Clone the repository
git clone https://github.com/fluidity-labs/metta-game-server.git
cd metta-game-server

# Install dependencies
pip install -r requirements.txt

# Run in websocket mode
python main.py

# Run in CLI mode
METTA_GAME_INPUT_MODE=cli python main.py
```

## Input Modes

Choose the active input transport at startup with `METTA_GAME_INPUT_MODE`:

- `websocket` (default): starts a websocket server and accepts commands from a web client.
- `cli`: reads commands from stdin.

Optional websocket settings:

- `METTA_GAME_WEBSOCKET_HOST` defaults to `127.0.0.1`
- `METTA_GAME_WEBSOCKET_PORT` defaults to `8765`
- Legacy `METTA_RIFT_*` environment variables are still accepted for backward compatibility.

## Websocket Messages

When `METTA_GAME_INPUT_MODE=websocket` or the variable is unset, the server accepts JSON messages only.

Request:

```json
{
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "command": "look around",
  "command_type": "natural_language"
}
```

Supported `command_type` values:

- `natural_language`
- `metta`

Examples:

```json
{
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "command": "pick up lantern",
  "command_type": "natural_language"
}
```

```json
{
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "command": "!(move player north)",
  "command_type": "metta"
}
```

Startup event:

```json
{
  "event": "startup",
  "metta_code": "..."
}
```

If the startup trigger produces messages, they are sent immediately after the `startup`
event as a normal `command_result`:

```json
{
  "event": "command_result",
  "queries": [
    {
      "command_type": "metta",
      "original_input": "!(trigger (Startup))",
      "matched_metta": "!(trigger (Startup))",
      "original_responses": [
        "(Response 100 \"You are in a cabin.\")"
      ],
      "responses": [
        "You are in a cabin."
      ]
    }
  ]
}
```

Command response:

```json
{
  "event": "command_result",
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "queries": [
    {
      "command_type": "natural_language",
      "original_input": "look around",
      "matched_metta": "!look",
      "original_responses": [
        "(Response 5 \"You are in a cabin.\")"
      ],
      "responses": [
        "You are in a cabin."
      ]
    },
    {
      "command_type": "metta",
      "original_input": "!(synchronize-tick)",
      "matched_metta": "!(synchronize-tick)",
      "original_responses": [],
      "responses": []
    }
  ]
}
```

Error event:

```json
{
  "event": "error",
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "error": "..."
}
```

Game won event:

```json
{
  "event": "game_won",
  "uuid": "123e4567-e89b-12d3-a456-426614174000"
}
```

Game over event:

```json
{
  "event": "game_over",
  "uuid": "123e4567-e89b-12d3-a456-426614174000"
}
```

## Tech Stack

[MeTTa](https://metta-lang.dev/) (Meta Type Talk) is a multi-paradigm language for declarative and functional computations over knowledge (meta)graphs.

[OpenCog Hyperon](https://hyperon.opencog.org/) is an ambitious open-source project aimed at creating an Artificial General Intelligence (AGI) framework, capable of human-level reasoning and beyond.

## License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for details.

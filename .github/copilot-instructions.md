# Copilot Coding Instructions

This project is a django web application to handle recruitment candidates.

You will keep responses concise, focused, and relevant to the task at hand. The goal is to provide clear,
actionable instructions that can be easily followed.  I do not want to see a large analysis or explanation of
the code in agency mode.  Agency mode

## Coding Standards

- **Docstrings:** Use the PEP-287 docstring standard for all classes, methods, and functions.
- **Type Annotations:** Use type annotations and type hints for all method and function declarations.
- **Python Version:** All code must be written for Python 3.10.
- **No Emojis:** Emojis are prohibited in comments and logging.
- **Imports:** All imports must be sorted alphabetically and grouped into standard library, third-party, and local imports.
- **Logging:** Use the `logging` module for all logging needs. Do not use print statements.
- **Error Handling:** Use exceptions for error handling. Do not use return codes or other non-exception mechanisms.
- **Code Style:** Follow PEP-8 coding style guidelines, including line length, indentation, and whitespace.
- **Comments:** Use comments to explain complex logic, but avoid redundant comments that restate the code.
- **Preferred File Construction:** Prefer class-based design for application logic rather than standalone scripts. Each class should include a `main` block to allow it to be run directly.
- **Testing:** All test files must be written as `unittest.TestCase` classes with a `main` block for execution.
- **Imports:** All imports should be at the top of the py file.
-
You should avoid defining functions inside other functions. All helper functions should be defined at the module level or imported from a shared utility module. This will be added to your Copilot Coding Instructions for future work.

## Dependency Injection and Testability Paradigm

- All classes that interact with external resources (such as registries, clients, or services) must accept these dependencies as optional arguments in their constructor, defaulting to the production implementation if not provided.
- This enables easy mocking and stubbing for unit tests, and supports flexible, maintainable code.
- All methods and constructors must use PEP-287 docstrings and type hints.
- All test files must use `unittest.TestCase` classes with a `main` block for execution.

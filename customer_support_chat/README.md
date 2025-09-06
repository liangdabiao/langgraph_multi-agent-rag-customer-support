# Customer Support Chat Module
This module powers a customer support chatbot designed to handle various workflows such as flight booking, hotel booking, car rentals, and excursion recommendations. It is structured using design patterns to enable easy maintenance, scalability, and adaptability to future changes. The chatbot's architecture allows for multi-assistant workflows, where each task is handled by a specialized assistant, ensuring a smooth user experience.

The core components include a ```state management system```, tools for interacting with different services, and a ```dynamic graph-based approach``` to managing conversations. Each assistant is designed to focus on a specific task, allowing for modular updates and improvements without affecting the overall system.


## Structure
```
customer_support_chat
├── README.md
├── __init__.py
├── app
│   ├── __init__.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── settings.py
│   │   └── state.py
│   ├── data
│   ├── graph.py
│   ├── main.py
│   └── services
│       ├── __init__.py
│       ├── assistants
│       │   ├── __init__.py
│       │   ├── assistant_base.py
│       │   ├── car_rental_assistant.py
│       │   ├── excursion_assistant.py
│       │   ├── flight_booking_assistant.py
│       │   ├── hotel_booking_assistant.py
│       │   └── primary_assistant.py
│       ├── embeddings
│       ├── tools
│       │   ├── __init__.py
│       │   ├── cars.py
│       │   ├── excursions.py
│       │   ├── flights.py
│       │   ├── hotels.py
│       │   └── lookup.py
│       ├── utils.py
│       └── vectordb
│           ├── __init__.py
│           ├── chunkenizer.py
│           ├── utils.py
│           └── vectordb.py
└── data
    ├── travel2.sqlite
    ├── travel2.sqlite.bkp
    ├── travel2.sqlite.bkp.zero
    └── user_test_fetch_data.sql
10 directories, 32 files
```

## Design
This module has been designed to function as a Python package, making it suitable for integration into larger platforms or automation frameworks like Airflow, Kubernetes, or CI/CD pipelines. The modular approach ensures that specific assistants or tools can be reused, adapted, or extended to meet evolving business requirements. Whether you need to add new booking services, update the interaction flow, or introduce new integrations, the underlying architecture supports these changes with minimal effort.


## Overview of the Customer Support Chat Module
The customer_support_chat module orchestrates a multi-agent system that handles various customer support tasks, such as booking flights, car rentals, hotels, and excursions. The system uses LangChain and LangGraph to build flexible workflows and assistants, allowing for efficient task delegation. Each assistant follows the same design pattern, making the system scalable and easy to extend with new assistants.

This section dives deeper into the main components of the system and their purpose.

## Main Files Overview
- ```assistant_base.py```
This file is the base structure for all specialized assistants and implements the Strategy Pattern. It provides a common framework that all assistants, such as flight booking or car rental, use to interact with the system.

-   ```Assistant Class```: Manages the core logic of how the assistants process tasks and user inputs. It ensures that tasks are completed or escalated when necessary.
-   ```CompleteOrEscalate Tool```: This tool is used by assistants to either complete the current task or escalate it to the primary assistant if further actions are needed.
- This file serves as the backbone of all assistant logic, ensuring consistency across different workflows.

- ```primary_assistant.py```
This file defines the Primary Assistant, which acts as a supervisor, delegating tasks to specialized assistants.

- ```Task Delegation Tools```: Models like ToFlightBookingAssistant, ToBookCarRental, etc., help route tasks to specialized assistants based on the user’s needs.
- ```primary_assistant_runnable```: Combines the primary prompt and tools to handle general inquiries. If the request involves specialized tasks, it delegates them to the appropriate assistant.
- This assistant follows the Chain of Responsibility Pattern, allowing for seamless delegation without exposing the underlying assistant structure to the user.

- ```main.py```
This file serves as the main orchestrator of the system. It sets up the environment, manages user input, and interacts with the graph to execute tasks.

- ```Graph Visualization```: The graph is generated and saved as an image for visual debugging and analysis.
- ```Interaction Loop```: The system enters a loop where it continuously listens for user inputs, processes them, and streams the responses from the graph.
- ```Interrupt Handling```: If the system requires sensitive actions like modifying bookings, it asks the user for confirmation, ensuring control over critical tasks.

- ```graph.py```
This file constructs the multi-agent workflow graph, where each assistant is represented as a sub-graph.

- ```Node Definitions```: Each assistant has its own entry, processing, and exit nodes that manage the task lifecycle.
- ```Routing Logic```: The system routes tasks to the relevant assistant based on the user's input and the tools needed to complete the task.
- ```Primary Assistant```: Handles general tasks and delegates specific ones to specialized assistants such as flight booking, car rentals, hotels, and excursions.
- ```Interrupt Management```: The graph includes interrupt nodes that pause execution when sensitive tools (like modifying a booking) are invoked, allowing the user to approve or deny actions.

This modular design allows the system to handle complex workflows efficiently while maintaining flexibility to add new capabilities easily. The system architecture makes it ideal for integrating with additional tools and assistants, allowing for scalable customer support automation.

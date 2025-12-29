# Technical Whitepaper: Compute Architecture Strategy

**Project:** CryptoFlow
**Module:** Infrastructure & DevOps
**Topic:** Serverless vs. Container Orchestration (Kubernetes) in HFT Context
**Status:** Approved Strategy

## 1. Executive Summary

This document outlines the architectural reasoning behind choosing Kubernetes (AKS) over Serverless (Azure Functions) for the core execution engine of CryptoFlow.

While Serverless offers simplicity and cost-savings for sporadic workloads, High-Frequency Trading (HFT) and AI-driven systems require low-latency, stateful connections, and guaranteed compute resources. This paper compares the available compute models and justifies the "Container-First" approach for our microservices topology.

## 2. The Compute Spectrum

To make an informed decision, we must understand the three primary layers of cloud compute:

### 2.1 Serverless (FaaS - Function as a Service)

*   **Examples:** Azure Functions, AWS Lambda.
*   **Model:** "Event-driven." Code sleeps until triggered (HTTP request, Database change).
*   **Billing:** Pay per millisecond of execution time.
*   **Lifecycle:** Ephemeral. The environment is created and destroyed automatically by the provider.

### 2.2 Container Orchestration (CaaS - Containers as a Service)

*   **Examples:** Azure Kubernetes Service (AKS), Amazon EKS.
*   **Model:** "Always-on." Containers run continuously on a cluster of managed Virtual Machines (Nodes).
*   **Billing:** Pay for the underlying Virtual Machines (Nodes) 24/7, regardless of traffic.
*   **Lifecycle:** Persistent. Containers restart only on failure or update.

### 2.3 Platform as a Service (PaaS)

*   **Examples:** Azure App Service, Azure Container Apps.
*   **Model:** A middle ground. Abstracts the server management but allows long-running processes.

## 3. The "HFT" Constraint Analysis

High-Frequency Trading imposes specific constraints that break standard web application patterns. We evaluated Serverless against these constraints:

### Constraint A: Latency & Cold Starts

*   **The Problem:** In trading, milliseconds equal money. An opportunity to arbitrage might exist for only 500ms.
*   **Serverless Failure Mode:** If a Serverless function hasn't run in the last 5-10 minutes, the cloud provider "freezes" it to save energy. The next request triggers a "Cold Start," where the system must boot a new micro-VM, download code, and start the process. This takes 200ms - 2000ms.
*   **Kubernetes Advantage:** Containers are "Hot." They are already loaded in RAM with socket connections open. Response time is effectively instantaneous (<10ms).

### Constraint B: Protocol Support (gRPC & WebSockets)

*   **The Problem:** Market Data feeds use Streaming protocols (WebSockets or gRPC streams) to push thousands of price updates per second. These require a persistent, long-lived TCP connection.
*   **Serverless Failure Mode:** Serverless functions are designed for "Request/Response" (HTTP). They typically have execution time limits (e.g., 5-10 minutes) and aggressively sever idle connections. You cannot keep a permanent WebSocket open to Binance from a Lambda function.
*   **Kubernetes Advantage:** A container can keep a gRPC stream open for days without interruption, processing distinct messages as they flow in.

### Constraint C: In-Memory State

*   **The Problem:** To make buy/sell decisions fast, the OrderService needs the current "Order Book" or "Portfolio State" accessible in RAM (L1/L2 Cache). Fetching this from a database (Disk/Network) for every single decision is too slow.
*   **Serverless Failure Mode:** Serverless is "Stateless." You cannot rely on variables persisting between function invocations. You are forced to fetch state from Redis/Postgres every single time, adding network latency (Round Trip Time).
*   **Kubernetes Advantage:** A container can load the Portfolio into a Python Class instance on startup and update it in real-time. The data is locally available in nanoseconds.

## 4. Architectural Decision: The Hybrid Approach

Based on the analysis above, CryptoFlow utilizes a Hybrid Architecture, using the right tool for the right job.

### 4.1 The Core (Kubernetes / AKS)

*   **Workload:** Market Data Ingestion, Order Execution, AI Agent (MCP), API Gateway.
*   **Reason:**
    *   Requires sub-millisecond latency.
    *   Maintains persistent connections (gRPC to internal services, WebSockets to Exchanges).
    *   Needs predictable CPU performance (no "noisy neighbor" issues).

### 4.2 The Auxiliaries (Serverless / Azure Functions)

*   **Workload:** End-of-Day Reporting, User Sign-up Emails, Data Archival.
*   **Reason:**
    *   These events happen infrequently (once a day or once an hour).
    *   Latency of 2 seconds is acceptable.
    *   Paying for a dedicated server 24/7 for a task that takes 5 seconds is waste.

## 5. Comparison Matrix

| Feature | Serverless (Azure Functions) | Kubernetes (AKS) | Impact on CryptoFlow |
| :--- | :--- | :--- | :--- |
| **Cost Model** | Pay-per-trigger | Pay-per-node (Hourly) | K8s is cheaper for high-volume, constant workloads (like market data). |
| **Startup Time** | Slow (Cold Starts) | Instant (Always On) | **Critical:** K8s ensures we don't miss market moves. |
| **State** | Stateless | Stateful (In-Memory) | K8s allows fast in-memory strategy calculations. |
| **Connectivity** | Short-lived HTTP | Long-lived TCP/gRPC | K8s is required for our MarketDataService streams. |
| **Ops Effort** | Low (No servers) | High (Cluster Mgmt) | We accept higher Ops effort to gain performance control. |

## 6. Conclusion

For CryptoFlow, "Serverless" is an implementation detail for background tasks, but Kubernetes is the strategic platform for the Trading Engine.

Moving to the cloud does not mean abandoning servers; it means managing them more intelligently. By containerizing our microservices into a Universal Image and orchestrating them with Kubernetes, we achieve the performance of a monolith with the scalability of the cloud.

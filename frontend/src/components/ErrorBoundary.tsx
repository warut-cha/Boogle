import React from "react";

type ErrorBoundaryProps = {
  children: React.ReactNode;
};

type ErrorBoundaryState = {
  hasError: boolean;
  errorMessage: string;
};

export default class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);

    this.state = {
      hasError: false,
      errorMessage: "",
    };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      errorMessage: error.message,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error("Dashboard crashed:", error, errorInfo);
  }

  render(): React.ReactNode {
    if (this.state.hasError) {
      return (
        <main
          style={{
            minHeight: "100vh",
            backgroundColor: "#0f1419",
            color: "#e6edf3",
            padding: "2rem",
            fontFamily:
              "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
          }}
        >
          <h1 style={{ color: "#f85149" }}>Dashboard error</h1>

          <p style={{ color: "#8b949e" }}>
            A frontend component crashed. This page is shown by the error
            boundary instead of a black screen.
          </p>

          <pre
            style={{
              backgroundColor: "#161b22",
              border: "1px solid #30363d",
              borderRadius: "8px",
              padding: "1rem",
              whiteSpace: "pre-wrap",
              color: "#ff7b72",
            }}
          >
            {this.state.errorMessage}
          </pre>

          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: "1rem",
              padding: "0.75rem 1rem",
              backgroundColor: "#238636",
              border: "none",
              borderRadius: "6px",
              color: "#fff",
              cursor: "pointer",
              fontWeight: 700,
            }}
          >
            Reload dashboard
          </button>
        </main>
      );
    }

    return this.props.children;
  }
}
import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

export default function App() {
  const [message, setMessage] = useState("loading...");

  useEffect(() => {
    fetch(`${API_BASE}/hello`)
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch(() => setMessage("API unreachable"));
  }, []);

  return (
    <main style={{ fontFamily: "sans-serif", padding: "2rem" }}>
      <h1>Exercise 1.1 — Multi-Service Docker Environment</h1>
      <p>API says: {message}</p>
    </main>
  );
}

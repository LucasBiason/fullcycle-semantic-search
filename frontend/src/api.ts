const API_URL = import.meta.env.VITE_API_URL || "";

export async function fetchHealth() {
  const res = await fetch(`${API_URL}/health`);
  if (!res.ok) throw new Error("Backend unavailable");
  return res.json();
}

export async function sendQuestion(question: string, k: number = 20) {
  const res = await fetch(`${API_URL}/api/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, k }),
  });
  if (!res.ok) throw new Error(`Error: ${res.status}`);
  return res.json();
}

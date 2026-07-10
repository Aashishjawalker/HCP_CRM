const BASE_URL = 'http://localhost:8000/api';

/**
 * POST /api/chat
 * Send a chat message and get back a structured response + form state
 */
export async function sendChatMessage(message) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) {
    throw new Error(`Chat API error: ${res.status} ${res.statusText}`);
  }
  return res.json(); // { response: string, formState: object }
}

/**
 * POST /api/transcribe
 * Upload audio file and get transcribed text.
 */
export async function transcribeAudio(audioBlob) {
  const formData = new FormData();
  formData.append('file', audioBlob, 'recording.webm');
  const res = await fetch(`${BASE_URL}/transcribe`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Transcribe error: ${res.status} ${err}`);
  }
  const data = await res.json();
  return data.text;
}

/**
 * POST /api/interactions
 * Submit structured form data directly (bypasses LLM agent).
 */
export async function createInteraction(data) {
  const res = await fetch(`${BASE_URL}/interactions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    throw new Error(`POST interaction error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

/**
 * GET /api/interactions
 * Fetch all logged interactions
 */
export async function getInteractions() {
  const res = await fetch(`${BASE_URL}/interactions`);
  if (!res.ok) {
    throw new Error(`GET interactions error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

/**
 * PUT /api/interactions/:id
 * Update an interaction
 */
export async function updateInteraction(id, data) {
  const res = await fetch(`${BASE_URL}/interactions/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    throw new Error(`PUT interaction error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

/**
 * DELETE /api/interactions/:id
 * Delete an interaction by ID.
 */
export async function deleteInteraction(id) {
  const res = await fetch(`${BASE_URL}/interactions/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error(`DELETE interaction error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

/**
 * GET /api/hcps
 * Fetch HCP list for reference
 */
export async function getHcps() {
  const res = await fetch(`${BASE_URL}/hcps`);
  if (!res.ok) {
    throw new Error(`GET hcps error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}
